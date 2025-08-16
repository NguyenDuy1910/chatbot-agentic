import { ComponentType } from 'react';
import { ChatPage, AdminPage, ConnectionsPage, LoginPage } from '@/pages';

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
  CHAT: '/chat',
  ADMIN: '/admin',
  CONNECTIONS: '/connections',
  LOGIN: '/login',
} as const;

// Route configurations
export const routeConfigs: RouteConfig[] = [
  {
    path: ROUTES.HOME,
    component: ChatPage,
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
    path: ROUTES.LOGIN,
    component: LoginPage,
  },
];
