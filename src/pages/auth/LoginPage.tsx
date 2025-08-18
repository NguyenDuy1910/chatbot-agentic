import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LoginForm } from '@/components/features/auth';
import { LoginCredentials, RegisterData } from '@/types/features/auth';
import { useAuth } from '@/contexts/AuthContext';
import { ROUTES } from '@/router/constants';

/**
 * Login page component
 * Handles user authentication with AuthContext integration
 */
export const LoginPage: React.FC = () => {
  const { login, register, loading, error, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get the intended destination from location state, default to home
  const from = (location.state as any)?.from || ROUTES.HOME;

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleLogin = async (credentials: LoginCredentials) => {
    try {
      await login(credentials);
      // Navigation will be handled by the useEffect above
    } catch (error) {
      // Error is handled by AuthContext and passed via error prop
      console.error('Login failed:', error);
    }
  };

  const handleRegister = async (data: RegisterData) => {
    try {
      await register(data);
      // Navigation will be handled by the useEffect above
    } catch (error) {
      // Error is handled by AuthContext and passed via error prop
      console.error('Registration failed:', error);
    }
  };

  return (
    <LoginForm
      onLogin={handleLogin}
      onRegister={handleRegister}
      loading={loading}
      error={error}
    />
  );
};

export default LoginPage;
