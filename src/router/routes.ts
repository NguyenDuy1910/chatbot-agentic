import { ComponentType } from 'react';
import {
  ChatPage, AdminPage, ConnectionsPage, LoginPage, MainPage,
  NotebooksPage, FilesPage, SettingsPage, DemoPage
} from '@/pages';

export interface RouteConfig {
  path: string;
  component: ComponentType;
  exact?: boolean;
  protected?: boolean;
  adminOnly?: boolean;
}

// Route constants
export const ROUTES = {
  HOME: '/',
  MAIN: '/',
  CHAT: '/chat',
  ADMIN: '/admin',
  CONNECTIONS: '/connections',
  NOTEBOOKS: '/notebooks',
  FILES: '/files',
  SETTINGS: '/settings',
  DEMO: '/demo',
  LOGIN: '/login',
} as const;

// Route configurations
export const routeConfigs: RouteConfig[] = [
  {
    path: ROUTES.HOME,
    component: MainPage,
    exact: true,
  },
  {
    path: ROUTES.CHAT,
    component: ChatPage,
    protected: true,
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
  },
];
