# 🚀 Quick Start Guide - Session Connection Management

## Khởi Chạy Ứng Dụng

### 1. Start Development Server

```bash
cd finx-ui
npm run dev
```

Ứng dụng sẽ chạy tại: `http://localhost:5173`

## Testing Flow

### ✅ Step 1: Test Login

1. Navigate to: `http://localhost:5173/login`
2. **Mock auth đã tắt** - cần login credentials thật
3. Default test credentials (nếu backend có):
   - Email: `demo@vikki.com`
   - Password: `demo123`
4. Click "Login"
5. Sau khi login thành công → redirect to home page

### ✅ Step 2: Test Session Connection Demo

1. Navigate to: `http://localhost:5173/demo`
2. Click tab "🔒 Session + Connections"
3. Xem authentication status
4. Click "Add Demo Connection" để test
5. Connections sẽ xuất hiện trong list
6. Refresh page → connections vẫn còn (sessionStorage)
7. Click "Logout" → connections bị xóa

### ✅ Step 3: Test Real Athena Connection

1. Navigate to: `http://localhost:5173/connections`
2. Click "New Connection"
3. Chọn "Athena" connection type
4. Nhập AWS credentials:
   - Region: `us-east-1`
   - Access Key ID
   - Secret Access Key
   - S3 Output Location
5. Click "Test Connection"
6. Nếu thành công → connection tự động save vào sessionStorage
7. Check "Session Connections" section trong ConnectionDashboard

### ✅ Step 4: Verify SessionStorage

Open browser DevTools Console:

```javascript
// Check saved connections
JSON.parse(sessionStorage.getItem('vikki_connections'))

// Should return array of connections:
// [
//   {
//     id: "conn_...",
//     name: "My Connection",
//     type: "athena",
//     config: {...},
//     metadata: {...},
//     lastUsed: "2025-10-18T..."
//   }
// ]
```

### ✅ Step 5: Test Logout & Clear

1. Click user menu (top right)
2. Click "Logout"
3. Check sessionStorage again:

```javascript
sessionStorage.getItem('vikki_connections') // Should return null
```

## Expected Behavior

### ✅ Login Flow
- User phải nhập credentials
- Token saved in cookie
- User data saved in localStorage
- Redirect to home after login

### ✅ Connection Flow
- Test connection → auto-save to sessionStorage
- Metadata (catalog, schema) được track
- Last used time được update
- Default connection được mark

### ✅ Logout Flow
- Clear auth token
- Clear user data from localStorage
- **Clear connections from sessionStorage**
- Redirect to login page

### ✅ Session Persistence
- Connections persist khi refresh page
- Connections persist trong cùng tab
- Connections **NOT** persist khi close tab
- Connections **NOT** share between tabs

## API Integration (Future)

Hiện tại connections chỉ cache ở client. Để implement backend:

### Backend Endpoints Needed

```typescript
// Save connection to backend
POST /api/connections/save
{
  name: string;
  type: string;
  config: {...};
  metadata: {...};
}

// Load user's saved connections
GET /api/connections/list

// Delete connection
DELETE /api/connections/:id

// Update connection
PUT /api/connections/:id
```

### Modified Flow with Backend

1. User tests connection → save to sessionStorage (immediate)
2. Option to "Save Permanently" → POST to backend
3. On login → GET connections from backend
4. Merge backend connections with session connections

## Troubleshooting

### ❌ "User must be authenticated"
- Ensure you're logged in
- Check localStorage for user data
- Check cookie for auth token

### ❌ Connections not saving
- Check browser console for errors
- Verify sessionStorage is enabled
- Check ConnectionProvider is in component tree

### ❌ Connections cleared unexpectedly
- Did you logout?
- Did you close and reopen the tab?
- Check sessionStorage manually

### ❌ Cannot connect to backend
- Ensure backend is running
- Check `.env.local` for `VITE_API_BASE_URL`
- Default: `http://localhost:8000`

## Demo URLs

- **Login:** `http://localhost:5173/login`
- **Demo Page:** `http://localhost:5173/demo`
- **Connections:** `http://localhost:5173/connections`
- **Home:** `http://localhost:5173/`

## Environment Variables

Check `.env.local`:

```bash
# Must be false to enable real login
VITE_ENABLE_MOCK_AUTH=false

# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Debug mode
VITE_ENABLE_DEBUG_MODE=true
```

## What to Check

✅ Browser console for logs:
- "🔓 Real API mode - clearing any existing auth data"
- "✅ Connection saved to session"
- "🗑️ Connection removed from session"

✅ Network tab:
- Login request: POST `/api/auths/signin`
- User info: GET `/api/auths/user`

✅ Application tab → Storage:
- **sessionStorage:** `vikki_connections`
- **localStorage:** `user`
- **Cookies:** `token`

## Success Criteria

✅ User can login with credentials
✅ Mock auth is disabled
✅ Connections save to sessionStorage after test
✅ Connections persist on page refresh
✅ Connections cleared on logout
✅ No compile errors
✅ Demo page works correctly

---

**Status:** ✅ Ready for Testing
**Last Updated:** October 18, 2025
