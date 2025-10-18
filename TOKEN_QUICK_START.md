# Quick Start Guide - Token Management

## 🚀 Cách Sử Dụng Nhanh

### 1. Login với Remember Me

```typescript
import { useAuth } from '@/contexts/AuthContext';

function LoginComponent() {
  const { login } = useAuth();
  
  const handleLogin = async () => {
    await login({
      email: 'user@example.com',
      password: 'password123',
      rememberMe: true  // ← Giữ đăng nhập vĩnh viễn
    });
  };
}
```

### 2. Login Chỉ Trong Session

```typescript
const handleLogin = async () => {
  await login({
    email: 'user@example.com',
    password: 'password123',
    rememberMe: false  // ← Logout khi đóng browser
  });
};
```

### 3. Kiểm Tra Token Status

```typescript
import { authAPI } from '@/lib/authAPI';

// Kiểm tra đã đăng nhập chưa
const isLoggedIn = authAPI.isAuthenticated();

// Kiểm tra token đã hết hạn chưa
const isExpired = authAPI.isTokenExpired();

// Kiểm tra cần refresh chưa
const needsRefresh = authAPI.needsRefresh();
```

### 4. Refresh Token Thủ Công

```typescript
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { refreshAuth } = useAuth();
  
  const handleRefresh = async () => {
    try {
      await refreshAuth();
      console.log('Token refreshed!');
    } catch (error) {
      console.error('Refresh failed, please login again');
    }
  };
}
```

### 5. API Calls (Tự Động Xử Lý Token)

```typescript
import { api } from '@/lib/api';

// API sẽ TỰ ĐỘNG:
// - Thêm Bearer token
// - Refresh token nếu hết hạn
// - Retry request sau khi refresh

async function fetchUserData() {
  try {
    const user = await api.get('/api/v1/users/me');
    return user;
  } catch (error) {
    // Lỗi đã được xử lý, chỉ cần show message
    console.error('Failed to fetch user');
  }
}
```

## ✨ Tính Năng Tự Động

### 1. Auto Token Refresh
Token sẽ **TỰ ĐỘNG** refresh trước 5 phút khi sắp hết hạn.

```
Login → Token expires in 24h → Auto-refresh after 23h 55m
```

### 2. Auto Retry on 401
Khi gặp lỗi 401, hệ thống **TỰ ĐỘNG**:
1. Refresh token
2. Retry request ban đầu
3. Return kết quả

```
API Call → 401 Error → Refresh Token → Retry → Success
```

### 3. Cross-Tab Sync
Token được sync giữa các tabs:
- Login ở tab A → Tất cả tabs đều login
- Logout ở tab B → Tất cả tabs đều logout

## 🔧 Testing

### Browser Console Testing

1. Mở browser console
2. Chạy các lệnh test:

```javascript
// Login với Remember Me
await tokenDemo.rememberMeLogin();

// Kiểm tra status
tokenDemo.checkStatus();

// Test API call
await tokenDemo.testAPI();

// Logout
await tokenDemo.logout();

// Chạy tất cả tests
await tokenDemo.runAll();
```

## 📱 UI Components

### Login Form với Remember Me

Form đã có sẵn checkbox Remember Me:

```tsx
<Checkbox
  checked={formData.rememberMe}
  onChange={(e) => handleInputChange('rememberMe', e.target.checked)}
>
  Remember me
</Checkbox>
```

## 🐛 Troubleshooting

### Token không tự động refresh?
1. Check console logs: `🔄 Auto-refreshing token...`
2. Check token expiry: `tokenDemo.checkStatus()`
3. Clear cache và login lại

### Bị logout khi đóng browser?
- Đảm bảo **Remember Me = true** khi login
- Check storage: `tokenDemo.testStorage()`

### API calls bị 401?
- Token sẽ tự động refresh và retry
- Nếu vẫn lỗi → Clear cache và login lại

## 💡 Best Practices

### ✅ DO
```typescript
// Luôn handle errors
try {
  await login(credentials);
} catch (error) {
  showError('Login failed');
}

// Check auth trước protected actions
if (!authAPI.isAuthenticated()) {
  navigate('/login');
  return;
}
```

### ❌ DON'T
```typescript
// Không hard-code remember me
await login(credentials, true); // Bad

// Không skip error handling
await login(credentials); // No try-catch!

// Không manually manage token expiry
// (Hệ thống đã tự động xử lý)
```

## 🎯 Common Use Cases

### 1. Protected Route
```typescript
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <Spinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  
  return children;
}
```

### 2. Conditional Rendering
```typescript
function Header() {
  const { isAuthenticated, user } = useAuth();
  
  return (
    <header>
      {isAuthenticated ? (
        <UserMenu user={user} />
      ) : (
        <LoginButton />
      )}
    </header>
  );
}
```

### 3. Auto-save với Token Check
```typescript
async function autoSave(data) {
  // Check token trước khi save
  if (authAPI.needsRefresh()) {
    await authAPI.refreshToken();
  }
  
  await api.post('/api/v1/save', data);
}
```

## 📊 Token Timing

```
Time:     0h      5h      10h     15h     20h     23h55m  24h
          │       │       │       │       │       │       │
Login ────┤                                       │       │
          │                                       │       │
Token Valid ──────────────────────────────────────┤       │
          │                                       │       │
Auto-Refresh ─────────────────────────────────────┘       │
          │                                               │
Token Expired ────────────────────────────────────────────┘
```

## 🎓 Learning Resources

1. **Full Documentation**: `TOKEN_MANAGEMENT_IMPROVEMENT.md`
2. **Demo File**: `src/demos/tokenManagementDemo.ts`
3. **Source Files**:
   - `src/lib/authAPI.ts` - Token management
   - `src/lib/api.ts` - API interceptor
   - `src/contexts/AuthContext.tsx` - Auth context

---

**Need Help?** Check console logs hoặc contact dev team!
