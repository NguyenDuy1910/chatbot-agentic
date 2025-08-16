import React from 'react';
import { Button } from '@/components/shared/ui/Button';
import { Menu, X } from 'lucide-react';

interface MobileMenuProps {
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export const MobileMenu: React.FC<MobileMenuProps> = ({ 
  isOpen, 
  onToggle, 
  children 
}) => {
  return (
    <>
      {/* Mobile Menu Button */}
      <div className="lg:hidden fixed top-4 right-4 z-50">
        <Button
          variant="outline"
          size="sm"
          onClick={onToggle}
          className="bg-background/80 backdrop-blur-sm"
        >
          {isOpen ? (
            <X className="h-4 w-4" />
          ) : (
            <Menu className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-background/80 backdrop-blur-sm">
          <div className="fixed inset-y-0 right-0 max-w-xs w-full bg-background border-l border-border shadow-xl">
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-border">
                <h2 className="text-lg font-semibold">Menu</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                {children}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
