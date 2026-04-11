# Quick API Testing Guide - cURL Commands

This document provides cURL commands to test all authentication endpoints.

## Setup

### 1. Start Backend
```bash
cd Backend
python main.py
# Server runs on http://localhost:8000
```

### 2. Verify Server is Running
```bash
curl http://localhost:8000/health
# Or check Swagger UI: http://localhost:8000/docs
```

---

## Authentication Endpoints

### 1. Setup First Admin (One-Time Only)

**Endpoint:** `POST /api/setup-admin`

```bash
curl -X POST http://localhost:8000/api/setup-admin \
  -H "Content-Type: application/json" \
  -d '{"email":"rishisingh9152@gmail.com","password":"Ripra@2622"}'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "rishisingh9152@gmail.com",
    "role": "admin"
  }
}
```

**Test Error Case (403 - if admin already exists):**
```bash
# Try running setup-admin again - should return 403
curl -X POST http://localhost:8000/api/setup-admin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin2@example.com","password":"Password123"}'

# Expected: {"detail":"Admin already exists. This endpoint is disabled."}
```

---

### 2. Register New User

**Endpoint:** `POST /api/auth/register`

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"Password123"}'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "newuser@example.com",
    "role": "user"
  }
}
```

**Test Error Case (400 - duplicate email):**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"Password456"}'

# Expected: {"detail":"Email already registered"}
```

---

### 3. Login User

**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"Password123"}'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "newuser@example.com",
    "role": "user"
  }
}
```

**Test Error Case (401 - wrong password):**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"WrongPassword"}'

# Expected: {"detail":"Invalid email or password"}
```

---

## Admin-Only Endpoints

### Prerequisites
Get admin token first:
```bash
# Save the token from /api/setup-admin response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Or login with admin credentials
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rishisingh9152@gmail.com","password":"Ripra@2622"}' \
  -s | grep -o '"access_token":"[^"]*"'
```

---

### 4. Get Admin Dashboard

**Endpoint:** `GET /api/admin/dashboard`

```bash
curl -X GET http://localhost:8000/api/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
{
  "total_users": 2,
  "admin_count": 1,
  "total_songs": 50,
  "total_sessions": 123,
  "completed_sessions": 110,
  "avg_rating": 4.5
}
```

**Test Error Case (403 - using user token):**
```bash
# Get user token first
USER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/admin/dashboard \
  -H "Authorization: Bearer $USER_TOKEN"

# Expected: {"detail":"Not authorized to access this resource"}
```

---

### 5. List All Users

**Endpoint:** `GET /api/admin/users`

```bash
# Get all users
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $TOKEN"

# With pagination
curl -X GET "http://localhost:8000/api/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "rishisingh9152@gmail.com",
    "role": "admin",
    "created_at": "2026-04-09T10:00:00.000Z"
  },
  {
    "_id": "507f1f77bcf86cd799439012",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "newuser@example.com",
    "role": "user",
    "created_at": "2026-04-09T10:05:00.000Z"
  }
]
```

---

### 6. List All Songs

**Endpoint:** `GET /api/admin/songs`

```bash
curl -X GET http://localhost:8000/api/admin/songs \
  -H "Authorization: Bearer $TOKEN"

# With pagination
curl -X GET "http://localhost:8000/api/admin/songs?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
[
  {
    "_id": "507f1f77bcf86cd799439013",
    "title": "Raga Bhairav",
    "raga": "Bhairav",
    "talaal": "Teental",
    "duration": 600,
    "uploaded_by": "admin",
    "created_at": "2026-04-01T00:00:00.000Z"
  },
  ...
]
```

---

### 7. Get Statistics

**Endpoint:** `GET /api/admin/stats`

```bash
curl -X GET http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
{
  "total_users": 2,
  "total_songs": 50,
  "total_sessions": 123,
  "completed_sessions": 110,
  "avg_session_duration": 45,
  "avg_rating": 4.5,
  "users_by_role": {
    "admin": 1,
    "user": 1
  }
}
```

---

### 8. Promote User to Admin

**Endpoint:** `POST /api/admin/promote`

```bash
curl -X POST http://localhost:8000/api/admin/promote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com"}'
```

**Expected Response (200):**
```json
{
  "message": "User promoted to admin",
  "user": {
    "email": "newuser@example.com",
    "role": "admin"
  }
}
```

---

### 9. Demote Admin to User

**Endpoint:** `POST /api/admin/demote`

```bash
curl -X POST http://localhost:8000/api/admin/demote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com"}'
```

**Expected Response (200):**
```json
{
  "message": "Admin demoted to user",
  "user": {
    "email": "newuser@example.com",
    "role": "user"
  }
}
```

**Test Error Case (400 - cannot demote last admin):**
```bash
curl -X POST http://localhost:8000/api/admin/demote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"rishisingh9152@gmail.com"}'

# Expected: {"detail":"Cannot demote the last admin in the system"}
```

---

### 10. Delete Song

**Endpoint:** `DELETE /api/admin/song/{song_id}`

```bash
# First get a song ID from /api/admin/songs
curl -X DELETE http://localhost:8000/api/admin/song/507f1f77bcf86cd799439013 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200):**
```json
{
  "message": "Song deleted successfully"
}
```

**Test Error Case (404 - song not found):**
```bash
curl -X DELETE http://localhost:8000/api/admin/song/507f1f77bcf86cd799439999 \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"detail":"Song not found"}
```

---

## Testing Bash Script

Create a file `test_auth.sh`:

```bash
#!/bin/bash

API="http://localhost:8000/api"

echo "=== Setup Admin ==="
ADMIN_RESPONSE=$(curl -s -X POST $API/setup-admin \
  -H "Content-Type: application/json" \
  -d '{"email":"rishisingh9152@gmail.com","password":"Ripra@2622"}')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Admin Token: ${ADMIN_TOKEN:0:50}..."

echo -e "\n=== Register User ==="
USER_RESPONSE=$(curl -s -X POST $API/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Password123"}')

USER_TOKEN=$(echo $USER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "User Token: ${USER_TOKEN:0:50}..."

echo -e "\n=== Get Admin Dashboard ==="
curl -s -X GET $API/admin/dashboard \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== List Users ==="
curl -s -X GET $API/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.[0:2]'

echo -e "\n=== Test Complete ==="
```

Run with:
```bash
bash test_auth.sh
```

---

## Troubleshooting

### "Connection refused"
- Backend is not running
- Start with: `python main.py` in Backend directory

### "Invalid token"
- Token may be expired (24 hours)
- Get a new token by logging in again

### "Not authorized"
- Using user token on admin endpoint
- Get admin token with admin credentials

### "Email already registered"
- Change email address or use different one

### "Admin already exists"
- First admin already created
- Use login endpoint instead to get token

---

## Token Inspection

To see what's in your JWT token, use an online tool or decode locally:

```bash
# Install jq first
# On Windows: choco install jq

curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rishisingh9152@gmail.com","password":"Ripra@2622"}' \
  | jq '.access_token' -r | cut -d'.' -f2 | base64 -d
```

This will show the token payload:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "rishisingh9152@gmail.com",
  "role": "admin",
  "exp": 1712688000
}
```

---

## Summary

All endpoints are now documented with:
- ✅ cURL commands ready to copy-paste
- ✅ Expected responses for success cases
- ✅ Error cases with expected HTTP status codes
- ✅ Token handling examples
- ✅ Pagination examples
- ✅ Testing bash script

Start the backend server and begin testing!

