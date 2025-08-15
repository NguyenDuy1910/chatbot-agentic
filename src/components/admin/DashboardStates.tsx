import React from 'react';
import { RefreshCw, Shield } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface LoadingStateProps {
  message?: string;
}

interface ErrorStateProps {
  message?: string;
  onRetry: () => void;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ 
  message = "Loading Vikki ChatBot Admin Dashboard..." 
}) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background via-background to-muted/10">
      <div className="text-center p-8">
        <div className="relative">
          <RefreshCw className="h-12 w-12 sm:h-16 sm:w-16 animate-spin mx-auto mb-6 text-primary" />
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-primary/5 rounded-full blur-xl"></div>
        </div>
        <div className="text-lg sm:text-xl font-medium text-foreground">
          {message}
        </div>
        <div className="mt-2 text-sm text-muted-foreground">
          Please wait while we prepare your dashboard...
        </div>
      </div>
    </div>
  );
};

export const ErrorState: React.FC<ErrorStateProps> = ({ 
  message = "Failed to load dashboard data",
  onRetry 
}) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background via-background to-muted/10">
      <div className="text-center p-8 max-w-md mx-auto">
        <div className="relative">
          <Shield className="h-12 w-12 sm:h-16 sm:w-16 mx-auto mb-6 text-red-500" />
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-red-500/5 rounded-full blur-xl"></div>
        </div>
        <div className="text-lg sm:text-xl font-medium text-foreground mb-2">
          {message}
        </div>
        <div className="text-sm text-muted-foreground mb-6">
          Something went wrong while loading the dashboard. Please try again.
        </div>
        <Button 
          onClick={onRetry} 
          className="w-full sm:w-auto"
          size="lg"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      </div>
    </div>
  );
};
