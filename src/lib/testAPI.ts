/**
 * API Integration Test Suite
 * Test all API integrations to ensure they work with the backend
 */

import { authAPI } from './authAPI';
import { connectionAPI } from './connectionAPI';
import { promptAPI } from './promptAPI';
import { chatAPI } from './chatAPI';
import { api } from './api';

export interface TestResult {
  name: string;
  success: boolean;
  error?: string;
  duration: number;
}

export interface TestSuite {
  name: string;
  results: TestResult[];
  totalTests: number;
  passedTests: number;
  failedTests: number;
  totalDuration: number;
}

class APITester {
  private async runTest(name: string, testFn: () => Promise<void>): Promise<TestResult> {
    const startTime = Date.now();
    
    try {
      await testFn();
      const duration = Date.now() - startTime;
      
      return {
        name,
        success: true,
        duration
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      
      return {
        name,
        success: false,
        error: error instanceof Error ? error.message : String(error),
        duration
      };
    }
  }

  async testHealthCheck(): Promise<TestResult> {
    return this.runTest('Health Check', async () => {
      const response = await api.get('/health');
      if (!response.status || response.status === 'unhealthy') {
        throw new Error('Health check failed');
      }
    });
  }

  async testAuthEndpoints(): Promise<TestResult[]> {
    const tests: TestResult[] = [];

    // Test signup (might fail if user exists, that's ok)
    tests.push(await this.runTest('Auth - Signup', async () => {
      try {
        await authAPI.register({
          name: 'Test User',
          email: 'test@example.com',
          password: 'testpass123',
          confirmPassword: 'testpass123'
        });
      } catch (error) {
        // If user already exists, that's fine for testing
        if (error instanceof Error && error.message.includes('already exists')) {
          return;
        }
        throw error;
      }
    }));

    // Test signin with demo credentials
    tests.push(await this.runTest('Auth - Signin', async () => {
      await authAPI.login({
        email: 'demo@vikki.com',
        password: 'demo123'
      });
    }));

    // Test get current user (requires authentication)
    tests.push(await this.runTest('Auth - Get Current User', async () => {
      await authAPI.getCurrentUser();
    }));

    return tests;
  }

  async testConnectionEndpoints(): Promise<TestResult[]> {
    const tests: TestResult[] = [];

    // Test get connections
    tests.push(await this.runTest('Connections - Get List', async () => {
      await connectionAPI.getConnections();
    }));

    // Test connection templates
    tests.push(await this.runTest('Connections - Get Templates', async () => {
      await connectionAPI.getConnectionTemplates();
    }));

    // Test connection stats
    tests.push(await this.runTest('Connections - Get Stats', async () => {
      await connectionAPI.getConnectionStats();
    }));

    return tests;
  }

  async testPromptEndpoints(): Promise<TestResult[]> {
    const tests: TestResult[] = [];

    // Test get prompts
    tests.push(await this.runTest('Prompts - Get List', async () => {
      await promptAPI.getPrompts();
    }));

    // Test get templates
    tests.push(await this.runTest('Prompts - Get Templates', async () => {
      await promptAPI.getTemplates();
    }));

    return tests;
  }

  async testChatEndpoints(): Promise<TestResult[]> {
    const tests: TestResult[] = [];

    // Test get chats
    tests.push(await this.runTest('Chats - Get List', async () => {
      await chatAPI.getChats();
    }));

    // Test get messages
    tests.push(await this.runTest('Messages - Get List', async () => {
      await chatAPI.getMessages();
    }));

    return tests;
  }

  async runAllTests(): Promise<TestSuite[]> {
    console.log('🧪 Starting API Integration Tests...');
    
    const suites: TestSuite[] = [];

    // Health Check
    const healthResult = await this.testHealthCheck();
    suites.push({
      name: 'Health Check',
      results: [healthResult],
      totalTests: 1,
      passedTests: healthResult.success ? 1 : 0,
      failedTests: healthResult.success ? 0 : 1,
      totalDuration: healthResult.duration
    });

    // Auth Tests
    const authResults = await this.testAuthEndpoints();
    suites.push({
      name: 'Authentication',
      results: authResults,
      totalTests: authResults.length,
      passedTests: authResults.filter(r => r.success).length,
      failedTests: authResults.filter(r => !r.success).length,
      totalDuration: authResults.reduce((sum, r) => sum + r.duration, 0)
    });

    // Connection Tests
    const connectionResults = await this.testConnectionEndpoints();
    suites.push({
      name: 'Connections',
      results: connectionResults,
      totalTests: connectionResults.length,
      passedTests: connectionResults.filter(r => r.success).length,
      failedTests: connectionResults.filter(r => !r.success).length,
      totalDuration: connectionResults.reduce((sum, r) => sum + r.duration, 0)
    });

    // Prompt Tests
    const promptResults = await this.testPromptEndpoints();
    suites.push({
      name: 'Prompts',
      results: promptResults,
      totalTests: promptResults.length,
      passedTests: promptResults.filter(r => r.success).length,
      failedTests: promptResults.filter(r => !r.success).length,
      totalDuration: promptResults.reduce((sum, r) => sum + r.duration, 0)
    });

    // Chat Tests
    const chatResults = await this.testChatEndpoints();
    suites.push({
      name: 'Chat & Messages',
      results: chatResults,
      totalTests: chatResults.length,
      passedTests: chatResults.filter(r => r.success).length,
      failedTests: chatResults.filter(r => !r.success).length,
      totalDuration: chatResults.reduce((sum, r) => sum + r.duration, 0)
    });

    return suites;
  }

  printResults(suites: TestSuite[]): void {
    console.log('\n📊 API Integration Test Results');
    console.log('================================');

    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;
    let totalDuration = 0;

    suites.forEach(suite => {
      console.log(`\n📁 ${suite.name}`);
      console.log(`   Tests: ${suite.totalTests} | Passed: ${suite.passedTests} | Failed: ${suite.failedTests} | Duration: ${suite.totalDuration}ms`);
      
      suite.results.forEach(result => {
        const status = result.success ? '✅' : '❌';
        const error = result.error ? ` (${result.error})` : '';
        console.log(`   ${status} ${result.name} (${result.duration}ms)${error}`);
      });

      totalTests += suite.totalTests;
      totalPassed += suite.passedTests;
      totalFailed += suite.failedTests;
      totalDuration += suite.totalDuration;
    });

    console.log('\n📈 Summary');
    console.log('===========');
    console.log(`Total Tests: ${totalTests}`);
    console.log(`Passed: ${totalPassed} (${Math.round((totalPassed / totalTests) * 100)}%)`);
    console.log(`Failed: ${totalFailed} (${Math.round((totalFailed / totalTests) * 100)}%)`);
    console.log(`Total Duration: ${totalDuration}ms`);
    
    if (totalFailed === 0) {
      console.log('\n🎉 All tests passed! API integration is working correctly.');
    } else {
      console.log('\n⚠️  Some tests failed. Check the errors above and ensure backend is running.');
    }
  }
}

export const apiTester = new APITester();

// Export for use in browser console or components
export const runAPITests = async (): Promise<void> => {
  const suites = await apiTester.runAllTests();
  apiTester.printResults(suites);
};
