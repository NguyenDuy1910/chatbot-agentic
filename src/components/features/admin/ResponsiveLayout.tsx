import React from 'react';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  className = "" 
}) => {
  return (
    <div className={`
      w-full 
      max-w-7xl 
      mx-auto 
      px-4 
      sm:px-6 
      lg:px-8 
      space-y-6
      ${className}
    `}>
      {children}
    </div>
  );
};
