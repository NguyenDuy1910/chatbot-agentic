import React, { useState } from 'react';
import { JuliusSidebar } from './WorkspaceSidebar';
import { JuliusMainContent } from './WorkspaceContent';
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
