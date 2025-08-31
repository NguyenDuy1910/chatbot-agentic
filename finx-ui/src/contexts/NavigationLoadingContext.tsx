import React, { createContext, useContext, useState, useCallback } from 'react';

interface NavigationLoadingContextType {
  isLoading: boolean;
  loadingText: string;
  startLoading: (text?: string) => void;
  stopLoading: () => void;
  setLoadingText: (text: string) => void;
}

const NavigationLoadingContext = createContext<NavigationLoadingContextType | undefined>(undefined);

interface NavigationLoadingProviderProps {
  children: React.ReactNode;
  defaultLoadingDuration?: number;
}

export const NavigationLoadingProvider: React.FC<NavigationLoadingProviderProps> = ({
  children,
  defaultLoadingDuration = 800
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Loading...');

  const startLoading = useCallback((text?: string) => {
    if (text) {
      setLoadingText(text);
    }
    setIsLoading(true);

    // Auto stop loading after default duration if not manually stopped
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, defaultLoadingDuration);

    return () => clearTimeout(timer);
  }, [defaultLoadingDuration]);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const updateLoadingText = useCallback((text: string) => {
    setLoadingText(text);
  }, []);

  const value = {
    isLoading,
    loadingText,
    startLoading,
    stopLoading,
    setLoadingText: updateLoadingText
  };

  return (
    <NavigationLoadingContext.Provider value={value}>
      {children}
    </NavigationLoadingContext.Provider>
  );
};

export const useNavigationLoading = () => {
  const context = useContext(NavigationLoadingContext);
  if (context === undefined) {
    throw new Error('useNavigationLoading must be used within a NavigationLoadingProvider');
  }
  return context;
};

export default NavigationLoadingContext;
