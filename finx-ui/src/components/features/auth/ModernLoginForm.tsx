import React, { useState } from 'react';
import { Button, Input, Checkbox } from '@heroui/react';
import { Eye, EyeOff, Mail, Lock, LogIn, UserPlus, Sparkles, Bot, MessageCircle } from 'lucide-react';
import { LoginCredentials, RegisterData } from '@/types/features/auth';

interface ModernLoginFormProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  onRegister: (data: RegisterData) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

export const ModernLoginForm: React.FC<ModernLoginFormProps> = ({
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
      console.error('Form submission error:', err);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen flex overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Left Side - Welcome Section with Curved Design */}
      <div className="hidden lg:flex lg:w-1/2 relative">
        {/* Curved Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700">
          {/* Organic Curved Shape */}
          <svg 
            className="absolute inset-0 w-full h-full" 
            viewBox="0 0 400 800" 
            preserveAspectRatio="xMidYMid slice"
          >
            <defs>
              <linearGradient id="curveGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(59, 130, 246, 0.9)" />
                <stop offset="50%" stopColor="rgba(147, 51, 234, 0.8)" />
                <stop offset="100%" stopColor="rgba(79, 70, 229, 0.9)" />
              </linearGradient>
            </defs>
            <path 
              d="M0,0 C150,100 250,200 400,150 L400,300 C250,350 150,450 0,400 Z" 
              fill="url(#curveGradient)" 
              opacity="0.7"
            />
            <path 
              d="M0,200 C200,250 300,350 400,300 L400,500 C300,550 200,650 0,600 Z" 
              fill="url(#curveGradient)" 
              opacity="0.5"
            />
            <path 
              d="M0,400 C150,450 250,550 400,500 L400,700 C250,750 150,850 0,800 Z" 
              fill="url(#curveGradient)" 
              opacity="0.6"
            />
          </svg>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="space-y-8">
            {/* Logo and Brand */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-4xl font-bold">Vikki AI</h1>
              </div>
              <p className="text-xl text-blue-100">
                Your intelligent chatbot companion
              </p>
            </div>

            {/* Features */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-xl bg-white/20 backdrop-blur-sm mt-1">
                  <MessageCircle className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Smart Conversations</h3>
                  <p className="text-blue-100">Engage in natural, intelligent conversations</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-xl bg-white/20 backdrop-blur-sm mt-1">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">AI-Powered Insights</h3>
                  <p className="text-blue-100">Get intelligent responses and recommendations</p>
                </div>
              </div>
            </div>

            {/* Decorative Elements */}
            <div className="flex gap-4 pt-8">
              <div className="w-16 h-1 bg-white/30 rounded-full"></div>
              <div className="w-8 h-1 bg-white/20 rounded-full"></div>
              <div className="w-4 h-1 bg-white/10 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center space-y-4">
            <div className="flex items-center justify-center gap-3">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Vikki AI
              </h1>
            </div>
          </div>

          {/* Form Header */}
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold text-gray-900">
              {isRegistering ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="text-gray-600">
              {isRegistering 
                ? 'Join Vikki AI and start your intelligent conversations'
                : 'Sign in to continue your AI-powered journey'
              }
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8">
            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Demo Credentials */}
            {!isRegistering && (
              <div className="mb-6 p-4 rounded-2xl bg-blue-50 border border-blue-200 text-blue-800 text-sm">
                <p className="font-medium mb-1">Test Credentials:</p>
                <p>Email: nguyenduy@gmail.com</p>
                <p>Password: 19102003</p>
              </div>
            )}

            {/* Toggle Buttons */}
            <div className="flex mb-8 p-1 bg-gray-100 rounded-2xl">
              <button
                type="button"
                onClick={() => setIsRegistering(false)}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-300 ${
                  !isRegistering
                    ? 'bg-white shadow-lg text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <LogIn className="h-4 w-4 inline mr-2" />
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setIsRegistering(true)}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-300 ${
                  isRegistering
                    ? 'bg-white shadow-lg text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <UserPlus className="h-4 w-4 inline mr-2" />
                Sign Up
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Field (Register only) */}
              {isRegistering && (
                <Input
                  label="Full Name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  variant="bordered"
                  radius="lg"
                  size="lg"
                  classNames={{
                    input: "text-gray-900",
                    inputWrapper: "border-gray-200 hover:border-blue-400 focus-within:border-blue-500"
                  }}
                  required
                />
              )}

              {/* Email Field */}
              <Input
                label="Email Address"
                placeholder="Enter your email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                startContent={<Mail className="h-4 w-4 text-gray-400" />}
                variant="bordered"
                radius="lg"
                size="lg"
                classNames={{
                  input: "text-gray-900",
                  inputWrapper: "border-gray-200 hover:border-blue-400 focus-within:border-blue-500"
                }}
                required
              />

              {/* Password Field */}
              <Input
                label="Password"
                placeholder="Enter your password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                startContent={<Lock className="h-4 w-4 text-gray-400" />}
                endContent={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
                variant="bordered"
                radius="lg"
                size="lg"
                classNames={{
                  input: "text-gray-900",
                  inputWrapper: "border-gray-200 hover:border-blue-400 focus-within:border-blue-500"
                }}
                required
              />

              {/* Confirm Password (Register only) */}
              {isRegistering && (
                <Input
                  label="Confirm Password"
                  placeholder="Confirm your password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  startContent={<Lock className="h-4 w-4 text-gray-400" />}
                  endContent={
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  }
                  variant="bordered"
                  radius="lg"
                  size="lg"
                  classNames={{
                    input: "text-gray-900",
                    inputWrapper: "border-gray-200 hover:border-blue-400 focus-within:border-blue-500"
                  }}
                  required
                />
              )}

              {/* Remember Me */}
              {!isRegistering && (
                <div className="flex items-center">
                  <Checkbox
                    isSelected={formData.rememberMe}
                    onValueChange={(checked) => handleInputChange('rememberMe', checked)}
                    size="sm"
                    color="primary"
                  >
                    <span className="text-sm text-gray-600">Remember me</span>
                  </Checkbox>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                isLoading={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
                size="lg"
              >
                {loading ? 'Please wait...' : (isRegistering ? 'Create Account' : 'Sign In')}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
