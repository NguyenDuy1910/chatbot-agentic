import { useNavigation } from './useNavigation';
import { navigateToPath, NavigationOptions } from '@/lib/navigation';

/**
 * Enhanced navigation hook with loading support
 */
export const useNavigationWithLoading = () => {
  const navigation = useNavigation();

  const navigateWithLoading = (path: string, options?: Partial<NavigationOptions>) => {
    const defaultOptions: NavigationOptions = {
      showLoading: true,
      loadingDuration: 600,
      ...options
    };

    // Get loading text based on path
    const getLoadingText = (targetPath: string): string => {
      const loadingTexts: { [key: string]: string } = {
        '/': 'Loading Home...',
        '/chat': 'Loading Chat Interface...',
        '/notebooks': 'Loading Notebooks...',
        '/files': 'Loading File Manager...',
        '/connections': 'Loading Data Connections...',
        '/settings': 'Loading Settings...',
        '/demo': 'Loading Demo...',
        '/admin': 'Loading Admin Dashboard...'
      };

      return loadingTexts[targetPath] || 'Loading...';
    };

    if (!defaultOptions.loadingText) {
      defaultOptions.loadingText = getLoadingText(path);
    }

    navigateToPath(path, defaultOptions);
  };

  const navigateWithCustomLoading = (
    path: string, 
    loadingText: string, 
    duration: number = 600
  ) => {
    navigateToPath(path, {
      showLoading: true,
      loadingText,
      loadingDuration: duration
    });
  };

  const navigateInstant = (path: string) => {
    navigateToPath(path, {
      showLoading: false
    });
  };

  return {
    ...navigation,
    navigateWithLoading,
    navigateWithCustomLoading,
    navigateInstant
  };
};

export default useNavigationWithLoading;
