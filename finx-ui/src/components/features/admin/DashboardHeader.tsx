import React from 'react';
import { Button } from '@/components/shared/ui/Button';
import { Crown, Download, RefreshCw } from 'lucide-react';

interface DashboardHeaderProps {
  onExportReport: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  onExportReport,
  onRefresh,
  isRefreshing
}) => {
  return (
    <div className="border-b border-border/50 bg-gradient-to-r from-background/80 to-muted/20 backdrop-blur-sm sticky top-0 z-10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="min-w-0 flex-1">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                <div className="flex items-center gap-3">
                  <Crown className="h-6 w-6 sm:h-8 sm:w-8 text-primary flex-shrink-0" />
                  <span className="truncate">Vikki ChatBot - Admin Dashboard</span>
                </div>
              </h1>
              <p className="text-muted-foreground mt-2 text-sm sm:text-base">
                Manage users, monitor Vikki chatbot interactions, and configure system settings
              </p>
            </div>
            
            <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
              <Button 
                variant="outline" 
                onClick={onExportReport}
                className="flex items-center gap-2 text-xs sm:text-sm"
                size="sm"
              >
                <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Export Report</span>
                <span className="sm:hidden">Export</span>
              </Button>
              <Button 
                onClick={onRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-2 text-xs sm:text-sm"
                size="sm"
              >
                <RefreshCw className={`h-3 w-3 sm:h-4 sm:w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Refresh</span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
