import React from 'react';
import { JuliusMainContent } from '@/components/features/main';

/**
 * Main page component - content only
 * This is the landing page with analysis templates and search functionality
 */
const MainPage: React.FC = () => {
  return <JuliusMainContent activeSection="notebooks" />;
};

export default MainPage;
