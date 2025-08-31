import React from 'react';
import { JuliusMainPage } from './JuliusMainPage';

/**
 * Demo component để test Julius AI Main Page
 * Có thể sử dụng component này để test UI trước khi tích hợp vào router
 */
export const JuliusMainPageDemo: React.FC = () => {
  return (
    <div className="h-screen w-full">
      <JuliusMainPage />
    </div>
  );
};

export default JuliusMainPageDemo;
