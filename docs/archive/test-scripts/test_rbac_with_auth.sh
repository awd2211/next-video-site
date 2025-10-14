#!/bin/bash
# Test RBAC endpoints with authentication

# Admin login credentials (adjust as needed)
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin123"

echo "=== Testing RBAC Endpoints ==="
echo ""

# 1. Login as admin
echo "1. Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  exit 1
fi

echo "✓ Got access token"
echo ""

# 2. Test roles endpoint
echo "2. Testing GET /api/v1/admin/rbac/roles"
curl -s "http://localhost:8000/api/v1/admin/rbac/roles" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -50

echo ""
echo ""

# 3. Test permissions endpoint
echo "3. Testing GET /api/v1/admin/rbac/permissions"
curl -s "http://localhost:8000/api/v1/admin/rbac/permissions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -50

echo ""
echo ""

# 4. Test admin users endpoint
echo "4. Testing GET /api/v1/admin/rbac/admin-users"
curl -s "http://localhost:8000/api/v1/admin/rbac/admin-users" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -50

echo ""
echo "=== Tests Complete ==="
