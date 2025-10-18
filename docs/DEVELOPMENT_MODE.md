# Development Mode - Authentication Bypass

## Overview

For easier local development and testing, you can disable authentication in the application. This allows you to access all API endpoints without needing to sign up, login, or manage tokens.

## ⚠️ WARNING

**This feature should ONLY be used in local development environments. NEVER enable this in production!**

## How to Enable

### Option 1: Environment Variable

Add the following line to your `.env` file:

```bash
DISABLE_AUTH=true
```

### Option 2: Export in Terminal

```bash
export DISABLE_AUTH=true
```

Then start your application normally:

```bash
cd finx-ai-service
python run.py
```

## What Happens When Authentication is Disabled

When `DISABLE_AUTH=true` is set:

1. **No login required** - All API endpoints become accessible without authentication
2. **Mock user created** - A mock admin user is automatically created with the following details:
   - **ID**: `dev-user-id`
   - **Email**: `dev@example.com`
   - **Name**: `Dev User`
   - **Role**: `admin`
   - **Profile Image**: `/user.png`

3. **All endpoints accessible** - You can access:
   - User endpoints
   - Admin endpoints
   - Chat endpoints
   - Connection endpoints
   - All other protected endpoints

## Testing APIs

With authentication disabled, you can test APIs directly:

### Using cURL

```bash
# Example: Get current user session (no token needed)
curl http://localhost:8000/api/v1/auth/session

# Example: Create a chat
curl -X POST http://localhost:8000/api/v1/chats \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'
```

### Using Postman or Thunder Client

Simply make requests without adding any Authorization headers.

### Using the Frontend

The frontend will work normally, but you won't need to login. The app will automatically use the mock user.

## Re-enabling Authentication

To re-enable authentication:

### Option 1: Update .env file

```bash
DISABLE_AUTH=false
```

Or simply remove/comment out the line:

```bash
# DISABLE_AUTH=true
```

### Option 2: Unset Environment Variable

```bash
unset DISABLE_AUTH
```

Then restart your application.

## Implementation Details

The authentication bypass is implemented in:

1. **Config** (`src/web/constants/config.py`):
   - Added `DISABLE_AUTH` flag to `SECURITY_CONFIG`

2. **Auth Utility** (`src/web/utils/auth.py`):
   - Modified `get_current_user()` function to return mock user when `DISABLE_AUTH=true`
   - All dependent functions (`get_verified_user`, `get_authenticated_user`, `get_admin_user`) inherit this behavior

## Use Cases

This feature is useful for:

- **Quick API testing** without dealing with tokens
- **Frontend development** without authentication flows
- **Integration testing** with simpler setup
- **Demo purposes** for quick showcases
- **Debugging** authentication-unrelated issues

## Best Practices

1. ✅ Use this only in local development
2. ✅ Keep `DISABLE_AUTH=false` in production config files
3. ✅ Add `.env` to `.gitignore` to avoid accidentally committing
4. ❌ Never commit code with hardcoded `DISABLE_AUTH=true`
5. ❌ Never use this in staging or production environments

## Troubleshooting

### Authentication still required after setting DISABLE_AUTH=true

1. Verify the environment variable is set:
   ```bash
   echo $DISABLE_AUTH
   ```

2. Restart the application after setting the variable

3. Check if you're using the correct `.env` file location

4. Verify the application is reading the environment variable:
   ```python
   from src.web.constants.config import SECURITY_CONFIG
   print(SECURITY_CONFIG.get("DISABLE_AUTH"))
   ```

### Frontend shows login page even with auth disabled

The frontend may need to be configured separately. Check the frontend configuration or API calls to ensure it's not enforcing client-side authentication.

## Security Note

The authentication bypass only affects the backend API. If you're concerned about security even in development:

1. Use a separate development database
2. Don't use real user data in development
3. Keep development environments isolated from production networks
4. Review code changes before deploying to ensure `DISABLE_AUTH` is not accidentally enabled

---

**Remember**: This is a development convenience feature. Always use proper authentication in production environments!
