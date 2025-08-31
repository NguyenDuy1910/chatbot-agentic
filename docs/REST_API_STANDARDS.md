# FinX Backend API - REST Standards & Conventions

## Overview

This document defines the REST API standards and conventions for the FinX Backend API. Following these guidelines ensures consistency, maintainability, and a great developer experience.

## Table of Contents

1. [URL Structure](#url-structure)
2. [HTTP Methods](#http-methods)
3. [Naming Conventions](#naming-conventions)
4. [Request/Response Format](#requestresponse-format)
5. [Error Handling](#error-handling)
6. [Status Codes](#status-codes)
7. [Authentication & Authorization](#authentication--authorization)
8. [Pagination](#pagination)
9. [Filtering & Searching](#filtering--searching)
10. [Versioning](#versioning)

## URL Structure

### Base URL
```
https://api.finx.com/api/v1
```

### Resource Naming
- Use **plural nouns** for collections: `/users`, `/chats`, `/messages`
- Use **lowercase** with **hyphens** for multi-word resources: `/connection-templates`
- Avoid verbs in URLs - use HTTP methods instead

### URL Patterns

#### Collection Operations
```
GET    /api/v1/users              # Get all users
POST   /api/v1/users              # Create new user
```

#### Individual Resource Operations
```
GET    /api/v1/users/{user_id}    # Get specific user
PUT    /api/v1/users/{user_id}    # Update specific user
DELETE /api/v1/users/{user_id}    # Delete specific user
```

#### Sub-resource Operations
```
GET    /api/v1/users/{user_id}/chats     # Get user's chats
POST   /api/v1/users/{user_id}/chats     # Create chat for user
GET    /api/v1/chats/{chat_id}/messages  # Get chat messages
```

#### Current User Context
```
GET    /api/v1/auth/me            # Get current user
PUT    /api/v1/auth/me/profile    # Update current user profile
GET    /api/v1/users/me/settings  # Get current user settings
```

## HTTP Methods

### Standard CRUD Operations

| Method | Purpose | Example |
|--------|---------|---------|
| `GET` | Retrieve resource(s) | `GET /users` |
| `POST` | Create new resource | `POST /users` |
| `PUT` | Update entire resource | `PUT /users/{id}` |
| `PATCH` | Partial update | `PATCH /users/{id}` |
| `DELETE` | Remove resource | `DELETE /users/{id}` |

### Action-Based Operations
For operations that don't fit CRUD, use `POST` with descriptive endpoints:

```
POST /api/v1/auth/login           # User login
POST /api/v1/auth/logout          # User logout
POST /api/v1/chats/{id}/share     # Share a chat
POST /api/v1/connections/{id}/test # Test connection
```

## Naming Conventions

### URL Parameters
- Use `snake_case` for query parameters: `?user_id=123&created_after=2024-01-01`
- Use descriptive names for path parameters: `{user_id}`, `{chat_id}`, `{message_id}`

### Function Names
Follow this pattern for FastAPI route functions:

```python
# Collection operations
async def get_all_users()          # GET /users
async def create_user()            # POST /users

# Individual resource operations  
async def get_user_by_id()         # GET /users/{user_id}
async def update_user_by_id()      # PUT /users/{user_id}
async def delete_user_by_id()      # DELETE /users/{user_id}

# Current user operations
async def get_current_user()       # GET /auth/me
async def update_current_user_profile() # PUT /auth/me/profile

# Action operations
async def login_user()             # POST /auth/login
async def test_connection_by_id()  # POST /connections/{id}/test
```

### Response Model Names
```python
# Single resource responses
UserResponse
ChatResponse  
MessageResponse

# Collection responses
UserListResponse
ChatListResponse

# Specialized responses
AuthenticationResponse
ConnectionTestResult
```

## Request/Response Format

### Request Body
Always use JSON for request bodies:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
```

### Response Structure

#### Success Responses
```json
// Single resource
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}

// Collection with metadata
{
  "data": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "has_more": true
}
```

#### Error Responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "message": "Email is required"
    }
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error context
    }
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Invalid input data
- `AUTHENTICATION_ERROR` - Invalid credentials
- `AUTHORIZATION_ERROR` - Insufficient permissions  
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `CONFLICT_ERROR` - Resource already exists
- `RATE_LIMIT_ERROR` - Too many requests
- `INTERNAL_SERVER_ERROR` - Server error

## Status Codes

### Success Codes
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE

### Client Error Codes
- `400 Bad Request` - Invalid request format/data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Valid auth but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource already exists or conflict
- `422 Unprocessable Entity` - Valid format but semantically incorrect
- `429 Too Many Requests` - Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Server temporarily unavailable

## Authentication & Authorization

### Authentication Header
```
Authorization: Bearer <jwt_token>
```

### Cookie-based Authentication
```
Cookie: token=<jwt_token>
```

### Permission Checking
```python
# Check user permissions before operations
if not check_user_permission(current_user, "read", resource):
    raise HTTPException(403, "Insufficient permissions")
```

## Pagination

### Query Parameters
```
GET /api/v1/users?page=1&limit=20&skip=0
```

### Response Format
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering & Searching

### Filter Parameters
```
GET /api/v1/chats?status=active&created_after=2024-01-01&folder_id=abc123
```

### Search Parameters
```
GET /api/v1/users?search=john&role=admin
```

### Sorting
```
GET /api/v1/chats?sort=created_at&order=desc
```

## Versioning

### URL Versioning (Current)
```
/api/v1/users
/api/v2/users  (future)
```

### Header Versioning (Alternative)
```
Accept: application/json; version=1
```

## Examples

### User Management API

```python
# Get all users with filtering
GET /api/v1/users?role=admin&active=true&page=1&limit=20

# Get specific user
GET /api/v1/users/123

# Update user
PUT /api/v1/users/123
{
  "name": "John Doe Updated",
  "email": "john.updated@example.com"
}

# Delete user
DELETE /api/v1/users/123
```

### Chat Management API

```python
# Get user's chats
GET /api/v1/chats?archived=false&pinned=true

# Create new chat
POST /api/v1/chats
{
  "title": "New Chat",
  "description": "Chat description"
}

# Share a chat
POST /api/v1/chats/abc123/share
{
  "share_id": "public-123"
}
```

### Authentication API

```python
# User registration
POST /api/v1/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}

# User login
POST /api/v1/auth/login
{
  "email": "john@example.com",
  "password": "securepassword"
}

# Get current user
GET /api/v1/auth/me

# Update profile
PUT /api/v1/auth/me/profile
{
  "name": "John Doe Updated",
  "profile_image_url": "https://example.com/image.jpg"
}
```

## Implementation Guidelines

### FastAPI Route Definition
```python
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user=Depends(get_verified_user)
):
    """Get a specific user by ID"""
    # Implementation
```

### Error Handling Pattern
```python
try:
    # Business logic
    pass
except HTTPException:
    # Re-raise HTTP exceptions
    raise
except Exception as e:
    log.error(f"Error in operation: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### Permission Checking Pattern
```python
# Check resource ownership
if resource.user_id != current_user.id and current_user.role != "admin":
    raise HTTPException(403, "Access denied")
```

## Validation

### Request Validation
Use Pydantic models for request validation:

```python
class UserCreateForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.USER
```

### Response Validation
Use Pydantic models for response validation:

```python
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    created_at: datetime
```

---

Following these conventions ensures a consistent, maintainable, and developer-friendly API that scales well with the application's growth.
