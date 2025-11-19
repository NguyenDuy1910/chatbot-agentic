/**
 * Token Management Demo & Testing
 * Demonstrates the improved token authentication features
 */

import { authAPI } from '@/lib/authAPI';
import { LoginCredentials } from '@/types/features/auth';

// ============================================================================
// 1. LOGIN WITH REMEMBER ME
// ============================================================================

export async function demoRememberMeLogin() {
  console.log('🔐 Demo: Login with Remember Me');
  
  // Remember Me = true (default) - Token lưu trong localStorage
  const credentials: LoginCredentials = {
    email: 'user@example.com',
    password: 'password123',
    rememberMe: true
  };
  
  try {
    const response = await authAPI.login(credentials, true);
    console.log('✅ Login successful:', response.user);
    console.log('📦 Token stored in localStorage');
    console.log('⏰ Token expires in:', response.expiresIn, 'seconds');
  } catch (error) {
    console.error('❌ Login failed:', error);
  }
}

// ============================================================================
// 2. LOGIN WITHOUT REMEMBER ME (SESSION ONLY)
// ============================================================================

export async function demoSessionOnlyLogin() {
  console.log('🔐 Demo: Session-Only Login');
  
  // Remember Me = false - Token lưu trong sessionStorage
  const credentials: LoginCredentials = {
    email: 'user@example.com',
    password: 'password123',
    rememberMe: false
  };
  
  try {
    const response = await authAPI.login(credentials, false);
    console.log('✅ Login successful:', response.user);
    console.log('📦 Token stored in sessionStorage (will be cleared when browser closes)');
  } catch (error) {
    console.error('❌ Login failed:', error);
  }
}

// ============================================================================
// 3. CHECK TOKEN STATUS
// ============================================================================

export function checkTokenStatus() {
  console.log('🔍 Checking Token Status');
  
  const isAuth = authAPI.isAuthenticated();
  const isExpired = authAPI.isTokenExpired();
  const needsRefresh = authAPI.needsRefresh();
  
  console.log('Authentication Status:', {
    isAuthenticated: isAuth,
    isExpired: isExpired,
    needsRefresh: needsRefresh,
  });
  
  if (isAuth && !isExpired) {
    console.log('✅ Token is valid');
  } else if (isAuth && isExpired) {
    console.log('⚠️ Token is expired - will auto-refresh on next API call');
  } else {
    console.log('❌ Not authenticated - please login');
  }
}

// ============================================================================
// 4. MANUAL TOKEN REFRESH
// ============================================================================

export async function demoManualRefresh() {
  console.log('🔄 Demo: Manual Token Refresh');
  
  try {
    const response = await authAPI.refreshToken();
    console.log('✅ Token refreshed successfully');
    console.log('👤 User:', response.user.name);
    console.log('⏰ New expiry:', response.expiresIn, 'seconds');
  } catch (error) {
    console.error('❌ Token refresh failed:', error);
    console.log('ℹ️ User needs to login again');
  }
}

// ============================================================================
// 5. SIMULATE TOKEN EXPIRY
// ============================================================================

export async function simulateTokenExpiry() {
  console.log('⏰ Simulating Token Expiry');
  
  // Set token with very short expiry (1 minute for testing)
  const token = localStorage.getItem('authToken');
  if (token) {
    const shortExpiry = 60; // 1 minute
    authAPI.setToken(token, undefined, shortExpiry, true);
    console.log('✅ Token expiry set to 1 minute');
    console.log('⏱️ Auto-refresh will happen in ~55 seconds');
    
    // Schedule check after 70 seconds
    setTimeout(() => {
      console.log('🔍 Checking status after 70 seconds...');
      checkTokenStatus();
    }, 70000);
  } else {
    console.log('❌ No token found - please login first');
  }
}

// ============================================================================
// 6. TEST STORAGE PERSISTENCE
// ============================================================================

export function testStoragePersistence() {
  console.log('📦 Testing Storage Persistence');
  
  const localToken = localStorage.getItem('authToken');
  const sessionToken = sessionStorage.getItem('authToken');
  const localUser = localStorage.getItem('user');
  const sessionUser = sessionStorage.getItem('user');
  
  console.log('Storage Status:', {
    localStorage: {
      hasToken: !!localToken,
      hasUser: !!localUser,
    },
    sessionStorage: {
      hasToken: !!sessionToken,
      hasUser: !!sessionUser,
    }
  });
  
  if (localToken) {
    console.log('✅ Using localStorage (Remember Me = true)');
    console.log('ℹ️ Session will persist after closing browser');
  } else if (sessionToken) {
    console.log('✅ Using sessionStorage (Remember Me = false)');
    console.log('⚠️ Session will be cleared when closing browser');
  } else {
    console.log('❌ No tokens found');
  }
}

// ============================================================================
// 7. TEST API WITH AUTO-REFRESH
// ============================================================================

export async function testAPIWithAutoRefresh() {
  console.log('🌐 Testing API with Auto-Refresh');
  
  const { api } = await import('@/lib/api');
  
  try {
    // Make an API call - will auto-refresh if token expired
    const response = await api.get('/api/v1/auth/me');
    console.log('✅ API call successful');
    console.log('👤 User:', response);
  } catch (error) {
    console.error('❌ API call failed:', error);
    
    if (error instanceof Error && error.message.includes('401')) {
      console.log('ℹ️ Token was invalid - auto-refresh attempted but failed');
      console.log('ℹ️ User needs to login again');
    }
  }
}

// ============================================================================
// 8. MONITOR TOKEN EVENTS
// ============================================================================

export function monitorTokenEvents() {
  console.log('👀 Monitoring Token Events');
  
  // Monitor localStorage changes (cross-tab sync)
  window.addEventListener('storage', (event) => {
    if (event.key === 'authToken') {
      if (event.newValue) {
        console.log('🔄 Token updated in another tab');
      } else {
        console.log('🚪 Token removed in another tab (logout)');
      }
    }
  });
  
  console.log('✅ Token event monitor started');
  console.log('ℹ️ Open console in another tab and login/logout to see events');
}

// ============================================================================
// 9. LOGOUT AND CLEANUP
// ============================================================================

export async function demoLogout() {
  console.log('🚪 Demo: Logout');
  
  try {
    await authAPI.logout();
    console.log('✅ Logged out successfully');
    console.log('🧹 All tokens and user data cleared');
    console.log('⏰ Auto-refresh timer cancelled');
  } catch (error) {
    console.error('❌ Logout failed:', error);
  }
}

// ============================================================================
// 10. RUN ALL DEMOS
// ============================================================================

export async function runAllDemos() {
  console.log('🎬 Running All Token Management Demos\n');
  
  // 1. Check initial status
  console.log('\n=== 1. Initial Status ===');
  checkTokenStatus();
  testStoragePersistence();
  
  // 2. Login with Remember Me
  console.log('\n=== 2. Login with Remember Me ===');
  await demoRememberMeLogin();
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 3. Check status after login
  console.log('\n=== 3. Status After Login ===');
  checkTokenStatus();
  testStoragePersistence();
  
  // 4. Test API call
  console.log('\n=== 4. Test API Call ===');
  await testAPIWithAutoRefresh();
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 5. Manual refresh
  console.log('\n=== 5. Manual Token Refresh ===');
  await demoManualRefresh();
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 6. Monitor events
  console.log('\n=== 6. Start Event Monitoring ===');
  monitorTokenEvents();
  
  // 7. Logout
  console.log('\n=== 7. Logout ===');
  await demoLogout();
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 8. Check final status
  console.log('\n=== 8. Final Status ===');
  checkTokenStatus();
  testStoragePersistence();
  
  console.log('\n✅ All demos completed!');
}

// ============================================================================
// BROWSER CONSOLE HELPERS
// ============================================================================

// Make functions available in browser console
if (typeof window !== 'undefined') {
  (window as any).tokenDemo = {
    rememberMeLogin: demoRememberMeLogin,
    sessionOnlyLogin: demoSessionOnlyLogin,
    checkStatus: checkTokenStatus,
    refresh: demoManualRefresh,
    simulateExpiry: simulateTokenExpiry,
    testStorage: testStoragePersistence,
    testAPI: testAPIWithAutoRefresh,
    monitor: monitorTokenEvents,
    logout: demoLogout,
    runAll: runAllDemos,
  };
  
  console.log('💡 Token Management Demo Functions Available!');
  console.log('Usage:');
  console.log('  tokenDemo.rememberMeLogin()  - Login with Remember Me');
  console.log('  tokenDemo.sessionOnlyLogin() - Login for session only');
  console.log('  tokenDemo.checkStatus()      - Check token status');
  console.log('  tokenDemo.refresh()          - Manual token refresh');
  console.log('  tokenDemo.simulateExpiry()   - Simulate token expiry');
  console.log('  tokenDemo.testStorage()      - Test storage persistence');
  console.log('  tokenDemo.testAPI()          - Test API with auto-refresh');
  console.log('  tokenDemo.monitor()          - Monitor token events');
  console.log('  tokenDemo.logout()           - Logout and cleanup');
  console.log('  tokenDemo.runAll()           - Run all demos');
}

export default {
  demoRememberMeLogin,
  demoSessionOnlyLogin,
  checkTokenStatus,
  demoManualRefresh,
  simulateTokenExpiry,
  testStoragePersistence,
  testAPIWithAutoRefresh,
  monitorTokenEvents,
  demoLogout,
  runAllDemos,
};
