import { ComponentType } from 'react';
import MainPage from '@/pages/main/MainPage';
import ChatPage from '@/pages/chat/ChatPage';
import AdminPage from '@/pages/admin/AdminPage';
import ConnectionsPage from '@/pages/connections/ConnectionsPage';
import LoginPage from '@/pages/auth/LoginPage';
import NotebooksPage from '@/pages/notebooks/NotebooksPage';
import FilesPage from '@/pages/files/FilesPage';
import SettingsPage from '@/pages/settings/SettingsPage';
import DemoPage from '@/pages/demo/DemoPage';
import { ROUTES } from './constants';

export interface RouteConfig {
  path: string;
  component: ComponentType;
  exact?: boolean;
  protected?: boolean;
  adminOnly?: boolean;
}

// Route configurations
export const routeConfigs: RouteConfig[] = [
  {
    path: ROUTES.CHAT,
    component: ChatPage,
    protected: true,
  },
  {
    path: ROUTES.HOME,
    component: MainPage,
    exact: true,
  },
  {
    path: ROUTES.ADMIN,
    component: AdminPage,
    protected: true,
    adminOnly: true,
  },
  {
    path: ROUTES.CONNECTIONS,
    component: ConnectionsPage,
    protected: true,
  },
  {
    path: ROUTES.NOTEBOOKS,
    component: NotebooksPage,
    protected: true,
  },
  {
    path: ROUTES.FILES,
    component: FilesPage,
    protected: true,
  },
  {
    path: ROUTES.SETTINGS,
    component: SettingsPage,
    protected: true,
  },
  {
    path: ROUTES.DEMO,
    component: DemoPage,
  },
  {
    path: ROUTES.LOGIN,
    component: LoginPage,
    exact: true,
  },
];
