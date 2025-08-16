import React from 'react';
import { ButtonDemo } from './ButtonDemo';

/**
 * Demo Launcher Component
 * Simple wrapper to test the ButtonDemo component directly
 * Can be used for quick testing without routing
 */
export const DemoLauncher: React.FC = () => {
  return (
    <div className="h-screen w-full">
      <ButtonDemo />
    </div>
  );
};

export default DemoLauncher;
