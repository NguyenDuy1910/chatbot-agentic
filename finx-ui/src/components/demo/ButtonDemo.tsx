import React, { useState } from 'react';
import { Button } from '@/components/shared/ui';
import { NavigationTest } from './NavigationTest';
import { LoadingAnimationDemo } from './LoadingAnimationDemo';
import {
  Plus,
  Download,
  Edit,
  Trash2,
  Settings,
  Search,
  Play,
  Pause,
  Save,
  Upload,
  Eye,
  Heart,
  Star,
  Share,
  Copy,
  Check,
  X,
  ArrowRight,
  ArrowLeft,
  ChevronDown,
  Loader2
} from 'lucide-react';

/**
 * Comprehensive Button Demo Component
 * Showcases all button types, variants, sizes, and styles available in the website
 */
export const ButtonDemo: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);

  const handleLoadingDemo = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Button Demo Showcase</h1>
          <p className="text-gray-600">
            Comprehensive demonstration of all button types, variants, sizes, and styles available in the website
          </p>
        </div>

        {/* Demo Controls */}
        <div className="bg-white p-4 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold mb-3">Demo Controls</h3>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={isDisabled}
                onChange={(e) => setIsDisabled(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Show Disabled State</span>
            </label>
            <Button onClick={handleLoadingDemo} size="sm">
              Test Loading State
            </Button>
          </div>
        </div>

        {/* Standard Button Component Variants */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h2 className="text-xl font-semibold mb-4">Standard Button Component</h2>
          <p className="text-gray-600 mb-6">
            Using the main Button component from <code className="bg-gray-100 px-2 py-1 rounded">@/components/shared/ui</code>
          </p>

          {/* Variants */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Variants</h3>
            <div className="flex flex-wrap gap-3">
              <Button variant="default" disabled={isDisabled}>Default</Button>
              <Button variant="outline" disabled={isDisabled}>Outline</Button>
              <Button variant="ghost" disabled={isDisabled}>Ghost</Button>
              <Button variant="destructive" disabled={isDisabled}>Destructive</Button>
            </div>
          </div>

          {/* Sizes */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Sizes</h3>
            <div className="flex flex-wrap items-center gap-3">
              <Button size="sm" disabled={isDisabled}>Small</Button>
              <Button size="default" disabled={isDisabled}>Default</Button>
              <Button size="lg" disabled={isDisabled}>Large</Button>
              <Button size="icon" disabled={isDisabled}>
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* With Icons */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">With Icons</h3>
            <div className="flex flex-wrap gap-3">
              <Button disabled={isDisabled}>
                <Plus className="h-4 w-4 mr-2" />
                Add New
              </Button>
              <Button variant="outline" disabled={isDisabled}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button variant="ghost" disabled={isDisabled}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant="destructive" disabled={isDisabled}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>

          {/* Loading State */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Loading State</h3>
            <div className="flex flex-wrap gap-3">
              <Button disabled={isLoading}>
                {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                {isLoading ? 'Loading...' : 'Click to Load'}
              </Button>
              <Button variant="outline" disabled={isLoading}>
                {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Save Changes
              </Button>
            </div>
          </div>
        </div>

        {/* Julius AI Button Styles */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h2 className="text-xl font-semibold mb-4">Julius AI Button Styles</h2>
          <p className="text-gray-600 mb-6">
            Custom Julius AI button classes from <code className="bg-gray-100 px-2 py-1 rounded">julius-ai-styles.css</code>
          </p>

          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Julius Button Variants</h3>
            <div className="flex flex-wrap gap-3">
              <button className="julius-btn julius-btn-primary" disabled={isDisabled}>
                <Plus className="h-4 w-4 mr-2" />
                Primary Button
              </button>
              <button className="julius-btn julius-btn-secondary" disabled={isDisabled}>
                <Settings className="h-4 w-4 mr-2" />
                Secondary Button
              </button>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Julius Buttons with Icons</h3>
            <div className="flex flex-wrap gap-3">
              <button className="julius-btn julius-btn-primary" disabled={isDisabled}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Files
              </button>
              <button className="julius-btn julius-btn-primary" disabled={isDisabled}>
                <Play className="h-4 w-4 mr-2" />
                Run
              </button>
              <button className="julius-btn julius-btn-secondary" disabled={isDisabled}>
                Refresh
              </button>
              <button className="julius-btn julius-btn-primary" disabled={isDisabled}>
                <Plus className="h-3 w-3 mr-1" />
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons Collection */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h2 className="text-xl font-semibold mb-4">Action Buttons Collection</h2>
          <p className="text-gray-600 mb-6">Common action buttons used throughout the application</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* File Actions */}
            <div>
              <h4 className="font-medium mb-3">File Actions</h4>
              <div className="space-y-2">
                <Button size="sm" className="w-full justify-start" disabled={isDisabled}>
                  <Eye className="h-3 w-3 mr-2" />
                  View
                </Button>
                <Button size="sm" variant="ghost" className="w-full justify-start" disabled={isDisabled}>
                  <Download className="h-3 w-3 mr-2" />
                  Download
                </Button>
                <Button size="sm" variant="ghost" className="w-full justify-start text-red-600 hover:text-red-700" disabled={isDisabled}>
                  <Trash2 className="h-3 w-3 mr-2" />
                  Delete
                </Button>
              </div>
            </div>

            {/* Media Controls */}
            <div>
              <h4 className="font-medium mb-3">Media Controls</h4>
              <div className="space-y-2">
                <Button size="sm" className="w-full justify-start" disabled={isDisabled}>
                  <Play className="h-3 w-3 mr-2" />
                  Play
                </Button>
                <Button size="sm" variant="outline" className="w-full justify-start" disabled={isDisabled}>
                  <Pause className="h-3 w-3 mr-2" />
                  Pause
                </Button>
                <Button size="sm" variant="ghost" className="w-full justify-start" disabled={isDisabled}>
                  <Save className="h-3 w-3 mr-2" />
                  Save
                </Button>
              </div>
            </div>

            {/* Social Actions */}
            <div>
              <h4 className="font-medium mb-3">Social Actions</h4>
              <div className="space-y-2">
                <Button size="sm" variant="ghost" className="w-full justify-start" disabled={isDisabled}>
                  <Heart className="h-3 w-3 mr-2" />
                  Like
                </Button>
                <Button size="sm" variant="ghost" className="w-full justify-start" disabled={isDisabled}>
                  <Star className="h-3 w-3 mr-2" />
                  Favorite
                </Button>
                <Button size="sm" variant="ghost" className="w-full justify-start" disabled={isDisabled}>
                  <Share className="h-3 w-3 mr-2" />
                  Share
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Button States & Animations */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h2 className="text-xl font-semibold mb-4">Button States & Animations</h2>
          <p className="text-gray-600 mb-6">Buttons with special effects and animations</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Hover Effects */}
            <div>
              <h4 className="font-medium mb-3">Hover Effects</h4>
              <div className="space-y-3">
                <Button className="hover-scale" disabled={isDisabled}>
                  Hover Scale Effect
                </Button>
                <Button className="button-glow" disabled={isDisabled}>
                  Glow Effect
                </Button>
                <Button className="ripple" disabled={isDisabled}>
                  Ripple Effect
                </Button>
              </div>
            </div>

            {/* State Buttons */}
            <div>
              <h4 className="font-medium mb-3">State Buttons</h4>
              <div className="space-y-3">
                <Button variant="outline" className="state-transition" disabled={isDisabled}>
                  <Check className="h-4 w-4 mr-2" />
                  Success State
                </Button>
                <Button variant="destructive" className="state-transition" disabled={isDisabled}>
                  <X className="h-4 w-4 mr-2" />
                  Error State
                </Button>
                <Button className="state-transition" disabled={isDisabled}>
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Next Step
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Navigation & Utility Buttons</h2>
          <p className="text-gray-600 mb-6">Buttons for navigation and utility functions</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Navigation */}
            <div>
              <h4 className="font-medium mb-3">Navigation</h4>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" disabled={isDisabled}>
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
                <Button size="sm" disabled={isDisabled}>
                  Next
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>

            {/* Dropdown */}
            <div>
              <h4 className="font-medium mb-3">Dropdown</h4>
              <Button variant="outline" disabled={isDisabled}>
                Options
                <ChevronDown className="h-4 w-4 ml-2" />
              </Button>
            </div>

            {/* Utility */}
            <div>
              <h4 className="font-medium mb-3">Utility</h4>
              <div className="flex space-x-2">
                <Button variant="ghost" size="sm" disabled={isDisabled}>
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </Button>
                <Button variant="ghost" size="sm" disabled={isDisabled}>
                  <Search className="h-4 w-4 mr-1" />
                  Search
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Test */}
        <NavigationTest />

        {/* Loading Animation Demo */}
        <LoadingAnimationDemo />
      </div>
    </div>
  );
};

export default ButtonDemo;
