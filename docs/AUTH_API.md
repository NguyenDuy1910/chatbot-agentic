# Authentication API Documentation

## Overview

The Authentication API provides endpoints for user registration, login, logout, and profile management.

## Base URL

```
http://localhost:8000/api/v1/auth
```

## Endpoints

### 1. User Registration

**POST** `/signup`

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "profile_image_url": "/user.png"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "pending",
  "profile_image_url": "/user.png",
  "token": "jwt-token-string",
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Email already taken
- `500 Internal Server Error`: Failed to create user

### 2. User Login

**POST** `/signin`

Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "pending",
  "profile_image_url": "/user.png",
  "token": "jwt-token-string",
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid credentials

### 3. User Logout

**POST** `/signout`

Logout user and clear authentication cookie.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully signed out"
}
```

### 4. Get Current User

**GET** `/user`

Get information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "pending",
  "profile_image_url": "/user.png"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Not authenticated

### 5. Update Profile

**POST** `/update/profile`

Update user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "profile_image_url": "/new_avatar.png"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "john@example.com",
  "name": "Updated Name",
  "role": "pending",
  "profile_image_url": "/new_avatar.png"
}
```

### 6. Update Password

**POST** `/update/password`

Update user password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "password": "current_password",
  "new_password": "new_secure_password"
}
```

**Response (200 OK):**
```json
true
```

**Error Responses:**
- `400 Bad Request`: Invalid current password
- `500 Internal Server Error`: Failed to update password

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After successful login or registration, you'll receive a token that must be included in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your-jwt-token>
```

## User Roles

- `pending`: Newly registered users (can access basic endpoints)
- `user`: Verified users (can access most features)
- `admin`: Administrative users (can access all features)

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server error

## Testing

Run the test suite to verify API functionality:

```bash
# Basic functionality tests
python tests/test_auth_api.py

# Edge case tests
python tests/test_auth_edge_cases.py
```

## Security Features

- Password hashing using bcrypt
- JWT token expiration (24 hours)
- Email uniqueness validation
- Role-based access control
- Secure cookie handling
