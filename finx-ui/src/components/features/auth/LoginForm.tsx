import React, { useState } from 'react';
import { Button, Input, Checkbox, Card, CardBody } from '@heroui/react';
import { Eye, EyeOff, Mail, Lock, LogIn, UserPlus, Sparkles, Bot, MessageCircle, Crown } from 'lucide-react';
import { LoginCredentials, RegisterData } from '@/types/features/auth';
import { cn } from '@/lib/utils';

interface LoginFormProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  onRegister: (data: RegisterData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onLogin,
  onRegister,
  loading = false,
  error
}) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    rememberMe: false
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (isRegistering) {
        if (formData.password !== formData.confirmPassword) {
          throw new Error('Passwords do not match');
        }
        await onRegister({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          confirmPassword: formData.confirmPassword
        });
      } else {
        await onLogin({
          email: formData.email,
          password: formData.password,
          rememberMe: formData.rememberMe
        });
      }
    } catch (err) {
      console.error('Authentication error:', err);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/10 p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Crown className="h-10 w-10 text-primary" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              Vikki ChatBot
            </h1>
          </div>
          <p className="text-muted-foreground">
            {isRegistering ? 'Create your account' : 'Welcome back'}
          </p>
        </div>

        {/* Login/Register Card */}
        <Card className="shadow-xl border-0 bg-background/80 backdrop-blur-sm">
          <CardBody className="space-y-4">
            <div className="space-y-1 pb-4">
              <h2 className="text-2xl font-semibold text-center">
                {isRegistering ? 'Sign Up' : 'Sign In'}
              </h2>
              <p className="text-sm text-muted-foreground text-center">
                {isRegistering
                  ? 'Enter your details to create an account'
                  : 'Enter your credentials to access your account'
                }
              </p>
            </div>
            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* Demo Credentials */}
            {!isRegistering && (
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-sm">
                <p className="font-medium mb-1">Demo Credentials:</p>
                <p>Email: demo@vikki.com</p>
                <p>Password: demo123</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name Field (Register only) */}
              {isRegistering && (
                <div className="space-y-2">
                  <label htmlFor="name" className="text-sm font-medium">
                    Full Name
                  </label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                    disabled={loading}
                    className="h-11"
                  />
                </div>
              )}

              {/* Email Field */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    required
                    disabled={loading}
                    className="h-11 pl-10"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    required
                    disabled={loading}
                    className="h-11 pl-10 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    disabled={loading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Confirm Password Field (Register only) */}
              {isRegistering && (
                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="text-sm font-medium">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      required
                      disabled={loading}
                      className="h-11 pl-10 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      disabled={loading}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              )}

              {/* Remember Me (Login only) */}
              {!isRegistering && (
                <div className="flex items-center space-x-2">
                  <input
                    id="rememberMe"
                    type="checkbox"
                    checked={formData.rememberMe}
                    onChange={(e) => handleInputChange('rememberMe', e.target.checked)}
                    disabled={loading}
                    className="h-4 w-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-0"
                  />
                  <label htmlFor="rememberMe" className="text-sm text-muted-foreground">
                    Remember me for 30 days
                  </label>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className={cn(
                  "w-full h-11 text-base font-medium",
                  "bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70",
                  "shadow-lg shadow-primary/30 transition-all duration-200"
                )}
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    {isRegistering ? 'Creating Account...' : 'Signing In...'}
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    {isRegistering ? <UserPlus className="h-4 w-4" /> : <LogIn className="h-4 w-4" />}
                    {isRegistering ? 'Create Account' : 'Sign In'}
                  </div>
                )}
              </Button>
            </form>

            {/* Toggle between Login/Register */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                {isRegistering ? 'Already have an account?' : "Don't have an account?"}
                <button
                  type="button"
                  onClick={() => {
                    setIsRegistering(!isRegistering);
                    setFormData({
                      name: '',
                      email: '',
                      password: '',
                      confirmPassword: '',
                      rememberMe: false
                    });
                  }}
                  disabled={loading}
                  className="ml-1 text-primary hover:text-primary/80 font-medium transition-colors"
                >
                  {isRegistering ? 'Sign In' : 'Sign Up'}
                </button>
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-8">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
};
