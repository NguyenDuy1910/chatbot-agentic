import React from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  ChatPage, AdminPage, ConnectionsPage, MainPage,
  NotebooksPage, FilesPage, SettingsPage, DemoPage
} from '@/pages';
import { ProtectedRoute } from '@/components/shared/auth';
import { ROUTES } from '@/router/routes';

/**
 * Main Content Router - Only renders the main content area using react-router-dom
 * Header, Sidebar, and Footer remain static
 */
export const MainContentRouter: React.FC = () => {
  return (
    <Routes>
      {/* Home/Main page */}
      <Route path={ROUTES.HOME} element={<MainPage />} />

      {/* Protected routes */}
      <Route
        path={ROUTES.CHAT}
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.ADMIN}
        element={
          <ProtectedRoute adminOnly>
            <AdminPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.CONNECTIONS}
        element={
          <ProtectedRoute>
            <ConnectionsPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.NOTEBOOKS}
        element={
          <ProtectedRoute>
            <NotebooksPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.FILES}
        element={
          <ProtectedRoute>
            <FilesPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.SETTINGS}
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />

      {/* Demo page - accessible to all authenticated users */}
      <Route
        path={ROUTES.DEMO}
        element={
          <ProtectedRoute>
            <DemoPage />
          </ProtectedRoute>
        }
      />

      {/* 404 page */}
      <Route
        path="*"
        element={
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-800">404 - Page Not Found</h1>
              <p className="text-gray-600">The page you're looking for doesn't exist.</p>
            </div>
          </div>
        }
      />
    </Routes>
  );
};

export default MainContentRouter;
