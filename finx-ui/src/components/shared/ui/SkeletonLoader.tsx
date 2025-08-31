import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonLoaderProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className,
  variant = 'rectangular',
  width,
  height,
  lines = 1
}) => {
  const baseClasses = 'skeleton-shimmer bg-gray-200 dark:bg-gray-700';

  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded',
    card: 'rounded-lg'
  };

  const style = {
    width: width || (variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'text' ? '16px' : variant === 'circular' ? '40px' : '200px')
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={cn(baseClasses, variantClasses.text)}
            style={{
              width: index === lines - 1 ? '75%' : '100%',
              height: '16px'
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cn(baseClasses, variantClasses[variant], className)}
      style={style}
    />
  );
};

// Predefined skeleton components
export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('p-4 border rounded-lg bg-white', className)}>
    <div className="flex items-center space-x-3 mb-4">
      <SkeletonLoader variant="circular" width={40} height={40} />
      <div className="flex-1">
        <SkeletonLoader variant="text" width="60%" />
        <SkeletonLoader variant="text" width="40%" className="mt-1" />
      </div>
    </div>
    <SkeletonLoader variant="text" lines={3} />
    <div className="flex justify-between items-center mt-4">
      <SkeletonLoader variant="rectangular" width={80} height={32} />
      <SkeletonLoader variant="rectangular" width={60} height={32} />
    </div>
  </div>
);

export const SkeletonTable: React.FC<{ rows?: number; columns?: number; className?: string }> = ({
  rows = 5,
  columns = 4,
  className
}) => (
  <div className={cn('space-y-3', className)}>
    {/* Header */}
    <div className="flex space-x-4">
      {Array.from({ length: columns }).map((_, index) => (
        <SkeletonLoader key={index} variant="text" width="100%" height={20} />
      ))}
    </div>
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="flex space-x-4">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <SkeletonLoader key={colIndex} variant="text" width="100%" height={16} />
        ))}
      </div>
    ))}
  </div>
);

export const SkeletonGrid: React.FC<{ items?: number; className?: string }> = ({
  items = 6,
  className
}) => (
  <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4', className)}>
    {Array.from({ length: items }).map((_, index) => (
      <SkeletonCard key={index} />
    ))}
  </div>
);

export default SkeletonLoader;
