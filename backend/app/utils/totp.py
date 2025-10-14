"""
TOTP (Time-based One-Time Password) utility for 2FA authentication
"""

import base64
import io
import json
import secrets
from typing import List, Tuple

import pyotp
import qrcode
from cryptography.fernet import Fernet

from app.config import settings


class TOTPManager:
    """Manager class for TOTP-based 2FA operations"""

    def __init__(self):
        # Use SECRET_KEY for encryption (in production, use a dedicated key)
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b"0"))
        self.cipher = Fernet(key)

    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret

        Returns:
            Base32-encoded secret string
        """
        return pyotp.random_base32()

    def encrypt_secret(self, secret: str) -> str:
        """
        Encrypt a TOTP secret for storage

        Args:
            secret: Plain TOTP secret

        Returns:
            Encrypted secret as string
        """
        return self.cipher.encrypt(secret.encode()).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt a stored TOTP secret

        Args:
            encrypted_secret: Encrypted secret string

        Returns:
            Decrypted plain secret
        """
        return self.cipher.decrypt(encrypted_secret.encode()).decode()

    def generate_qr_code(self, secret: str, user_email: str, issuer: str = "VideoSite Admin") -> bytes:
        """
        Generate QR code for TOTP setup

        Args:
            secret: TOTP secret
            user_email: User's email (used as account identifier)
            issuer: Service name (default: VideoSite Admin)

        Returns:
            PNG image bytes of QR code
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name=issuer)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Convert to image bytes
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def verify_token(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """
        Verify a TOTP token

        Args:
            secret: TOTP secret (plain or encrypted)
            token: 6-digit token from authenticator app
            valid_window: Number of intervals to check before/after (default: 1)

        Returns:
            True if token is valid, False otherwise
        """
        # Try to decrypt if it looks encrypted
        try:
            decrypted = self.decrypt_secret(secret)
            secret = decrypted
        except Exception:
            # If decryption fails, assume it's already plain
            pass

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)

    def generate_backup_codes(self, count: int = 8) -> List[str]:
        """
        Generate backup codes for account recovery

        Args:
            count: Number of backup codes to generate (default: 8)

        Returns:
            List of backup codes (format: XXXX-XXXX)
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    def encrypt_backup_codes(self, codes: List[str]) -> str:
        """
        Encrypt backup codes for storage

        Args:
            codes: List of backup codes

        Returns:
            Encrypted JSON string
        """
        json_codes = json.dumps(codes)
        return self.cipher.encrypt(json_codes.encode()).decode()

    def decrypt_backup_codes(self, encrypted_codes: str) -> List[str]:
        """
        Decrypt stored backup codes

        Args:
            encrypted_codes: Encrypted JSON string

        Returns:
            List of backup codes
        """
        decrypted = self.cipher.decrypt(encrypted_codes.encode()).decode()
        return json.loads(decrypted)

    def verify_backup_code(self, encrypted_codes: str, code: str) -> Tuple[bool, str | None]:
        """
        Verify a backup code and remove it from the list

        Args:
            encrypted_codes: Encrypted backup codes JSON
            code: Backup code to verify

        Returns:
            Tuple of (is_valid, updated_encrypted_codes or None)
        """
        codes = self.decrypt_backup_codes(encrypted_codes)
        code_upper = code.upper().strip()

        if code_upper in codes:
            # Remove used code
            codes.remove(code_upper)
            # Re-encrypt updated list
            updated_encrypted = self.encrypt_backup_codes(codes)
            return True, updated_encrypted
        return False, None

    def get_remaining_backup_codes_count(self, encrypted_codes: str) -> int:
        """
        Get count of remaining backup codes

        Args:
            encrypted_codes: Encrypted backup codes JSON

        Returns:
            Number of remaining codes
        """
        try:
            codes = self.decrypt_backup_codes(encrypted_codes)
            return len(codes)
        except Exception:
            return 0


# Singleton instance
totp_manager = TOTPManager()
