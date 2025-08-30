# API Migration Guide: REST Naming Convention Updates

## Overview

This document outlines the changes made to the FinX Backend API to follow proper REST API naming conventions. The changes focus on standardizing endpoint names, parameter naming, and function names to be more intuitive and RESTful.

## Major Changes

### 1. Authentication Endpoints (`/api/v1/auth`)

#### Endpoint Changes
- ✅ `POST /signup` → `POST /register`
- ✅ `POST /signin` → `POST /login` 
- ✅ `POST /signout` → `POST /logout`
- ✅ `GET /user` → `GET /me`
- ✅ `PUT /profile` → `PUT /me/profile`
- ✅ `PUT /password` → `PUT /me/password`

#### Function Name Changes
- ✅ `signup()` → `register_user()`
- ✅ `signin()` → `login_user()`
- ✅ `signout()` → `logout_user()`
- ✅ `get_session_user()` → `get_current_user_session()`
- ✅ `update_profile()` → `update_user_profile()`
- ✅ `update_password()` → `update_user_password()`

### 2. User Management Endpoints (`/api/v1/users`)

#### Function Name Changes
- ✅ `get_users()` → `get_all_users()`
- ✅ `get_user_groups()` → `get_current_user_groups()`
- ✅ `get_user_permissisions()` → `get_current_user_permissions()`
- ✅ `get_user_permissions()` → `get_current_user_permissions_detailed()`
- ✅ `update_user_permissions()` → `update_current_user_permissions()`
- ✅ `update_user_role()` → `update_user_role_by_id()`
- ✅ `get_user_settings_by_session_user()` → `get_current_user_settings()`
- ✅ `update_user_settings_by_session_user()` → `update_current_user_settings()`
- ✅ `get_user_info_by_session_user()` → `get_current_user_info()`
- ✅ `update_user_info_by_session_user()` → `update_current_user_info()`

#### Parameter Name Changes
- ✅ `/{id}/role` → `/{user_id}/role`
- ✅ Function parameter `id` → `user_id` where applicable

### 3. Chat Management Endpoints (`/api/v1/chats`)

#### Function Name Changes
- ✅ `get_chats()` → `get_user_chats()`
- ✅ `get_chat()` → `get_chat_by_id()`
- ✅ `update_chat()` → `update_chat_by_id()`
- ✅ `delete_chat()` → `delete_chat_by_id()`
- ✅ `toggle_chat_archive()` → `toggle_chat_archive_status()`
- ✅ `toggle_chat_pin()` → `toggle_chat_pin_status()`
- ✅ `share_chat()` → `share_chat_by_id()`

#### Parameter Name Changes
- ✅ `/{id}` → `/{chat_id}` for all chat-specific operations
- ✅ Function parameter `id` → `chat_id` throughout

### 4. Message Management Endpoints (`/api/v1/messages`)

#### Function Name Changes
- ✅ `get_messages()` → `get_user_messages()`
- ✅ `get_message()` → `get_message_by_id()`
- ✅ `update_message()` → `update_message_by_id()`
- ✅ `delete_message()` → `delete_message_by_id()`

#### Parameter Name Changes
- ✅ `/{id}` → `/{message_id}` for message-specific operations
- ✅ Function parameter `id` → `message_id` throughout

## REST API Best Practices Implemented

### 1. Resource-Based URLs
- ✅ URLs represent resources (nouns) rather than actions (verbs)
- ✅ Consistent use of plural nouns for collection endpoints

### 2. HTTP Methods Usage
- ✅ `GET` for retrieving data
- ✅ `POST` for creating resources
- ✅ `PUT` for updating resources
- ✅ `DELETE` for removing resources

### 3. Consistent Parameter Naming
- ✅ `{resource_id}` format for path parameters (e.g., `user_id`, `chat_id`, `message_id`)
- ✅ Clear, descriptive parameter names

### 4. Function Naming Conventions
- ✅ `get_{resource}_by_id()` for retrieving single resources
- ✅ `get_user_{resources}()` for user-specific collections
- ✅ `update_{resource}_by_id()` for updating resources
- ✅ `delete_{resource}_by_id()` for deleting resources

### 5. Self-Descriptive Endpoints
- ✅ `/me` for current user context
- ✅ `/me/profile`, `/me/settings`, `/me/password` for user-specific operations

## Migration Steps for Frontend

### 1. Update API Calls

#### Authentication
```typescript
// OLD
POST /api/v1/auth/signup
POST /api/v1/auth/signin
POST /api/v1/auth/signout
GET /api/v1/auth/user
PUT /api/v1/auth/profile
PUT /api/v1/auth/password

// NEW
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET /api/v1/auth/me
PUT /api/v1/auth/me/profile
PUT /api/v1/auth/me/password
```

#### Users
```typescript
// OLD
PUT /api/v1/users/{id}/role
GET /api/v1/users/groups
GET /api/v1/users/permissions

// NEW
PUT /api/v1/users/{user_id}/role
GET /api/v1/users/me/groups
GET /api/v1/users/me/permissions
```

#### Chats
```typescript
// OLD
GET /api/v1/chats/{id}
PUT /api/v1/chats/{id}
DELETE /api/v1/chats/{id}
PUT /api/v1/chats/{id}/archive
PUT /api/v1/chats/{id}/pin
POST /api/v1/chats/{id}/share

// NEW
GET /api/v1/chats/{chat_id}
PUT /api/v1/chats/{chat_id}
DELETE /api/v1/chats/{chat_id}
PUT /api/v1/chats/{chat_id}/archive
PUT /api/v1/chats/{chat_id}/pin
POST /api/v1/chats/{chat_id}/share
```

#### Messages
```typescript
// OLD
GET /api/v1/messages/{id}
PUT /api/v1/messages/{message_id}
DELETE /api/v1/messages/{message_id}

// NEW
GET /api/v1/messages/{message_id}
PUT /api/v1/messages/{message_id}
DELETE /api/v1/messages/{message_id}
```

### 2. Update TypeScript Types/Interfaces

Update any hardcoded endpoint strings and parameter names in your frontend code.

### 3. Test All API Integrations

After making the changes, ensure all API calls work correctly with the new endpoints.

## Backward Compatibility

⚠️ **Breaking Changes**: These are breaking changes that require frontend updates.

## Benefits of These Changes

1. **Improved Developer Experience**: More intuitive and predictable API endpoints
2. **Better Documentation**: Self-documenting endpoint names
3. **Industry Standards**: Follows REST API best practices
4. **Consistency**: Uniform naming conventions across all endpoints
5. **Scalability**: Easier to extend and maintain

## Additional Improvements Made

1. **Error Handling**: Consistent error responses across all endpoints
2. **Status Codes**: Proper HTTP status codes for different scenarios
3. **Response Models**: Consistent response structure
4. **Input Validation**: Enhanced request validation
5. **Permission Checks**: Improved authorization logic

## Files Modified

- `backend/finx/routers/auth.py`
- `backend/finx/routers/users.py`
- `backend/finx/routers/chats.py`
- `backend/finx/routers/messages.py`

## Next Steps

1. Update frontend API calls to use new endpoints
2. Update API documentation
3. Run comprehensive tests
4. Update any API client libraries
5. Communicate changes to development team

---

For any questions or issues with the migration, please refer to the updated API documentation or contact the backend development team.
