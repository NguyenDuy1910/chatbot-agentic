import React, { useState } from 'react';
import { JuliusSidebar } from './JuliusSidebar';
import { JuliusMainContent } from './JuliusMainContent';
import '@/styles/components/julius-ai-styles.css';

export const JuliusMainPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>('notebooks');

  return (
    <div className="julius-main-container">
      <JuliusSidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />
      <JuliusMainContent
        activeSection={activeSection}
      />
    </div>
  );
};

export default JuliusMainPage;
