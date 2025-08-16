import React from 'react';
import { LoginForm } from '@/components/features/auth';
import { LoginCredentials, RegisterData } from '@/types/features/auth';

/**
 * Login page component
 * Handles user authentication
 */
export const LoginPage: React.FC = () => {
  const handleLogin = async (credentials: LoginCredentials) => {
    // TODO: Implement actual login logic
    console.log('Login attempt:', credentials);
  };

  const handleRegister = async (data: RegisterData) => {
    // TODO: Implement actual registration logic
    console.log('Register attempt:', data);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <LoginForm onLogin={handleLogin} onRegister={handleRegister} />
      </div>
    </div>
  );
};

export default LoginPage;
