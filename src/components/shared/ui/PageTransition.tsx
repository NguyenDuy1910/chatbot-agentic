import React, { useState, useEffect } from 'react';
import { LoadingSpinner } from './LoadingSpinner';
import { cn } from '@/lib/utils';

interface PageTransitionProps {
  children: React.ReactNode;
  isLoading?: boolean;
  loadingText?: string;
  className?: string;
  transitionDuration?: number;
}

export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  isLoading = false,
  loadingText = 'Loading...',
  className,
  transitionDuration = 300
}) => {
  const [isVisible, setIsVisible] = useState(!isLoading);
  const [showContent, setShowContent] = useState(!isLoading);

  useEffect(() => {
    if (isLoading) {
      setIsVisible(false);
      setShowContent(false);
    } else {
      // Small delay to ensure smooth transition
      const timer = setTimeout(() => {
        setShowContent(true);
        setIsVisible(true);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className={cn(
        'min-h-screen flex items-center justify-center bg-gray-50',
        'transition-opacity duration-300 ease-in-out',
        className
      )}>
        <LoadingSpinner size="lg" text={loadingText} />
      </div>
    );
  }

  return (
    <div
      className={cn(
        'transition-all ease-in-out',
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
        className
      )}
      style={{ transitionDuration: `${transitionDuration}ms` }}
    >
      {showContent && children}
    </div>
  );
};

export default PageTransition;
