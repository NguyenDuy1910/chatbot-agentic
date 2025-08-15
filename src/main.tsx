import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { AdminApp } from './AdminApp.tsx'
import './index.css'

// Simple routing based on URL path
const AppRouter: React.FC = () => {
  const path = window.location.pathname;
  
  if (path.startsWith('/admin')) {
    return <AdminApp />;
  }
  
  return <App />;
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>,
)
