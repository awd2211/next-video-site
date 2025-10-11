"""
Captcha API endpoints
"""

from fastapi import APIRouter, Response

from app.utils.captcha import captcha_manager

router = APIRouter()


@router.get("/")
async def generate_captcha():
    """
    Generate a new captcha and return as PNG image

    Response headers include X-Captcha-ID for validation
    """
    captcha_id, image_bytes = await captcha_manager.generate_captcha()

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"X-Captcha-ID": captcha_id},
    )
