import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { AdminApp } from './AdminApp.tsx'
import './index.css'

// Enhanced routing with URL parameter management
const AppRouter: React.FC = () => {
  const path = window.location.pathname;
  
  // Admin routes with sub-pages
  if (path.startsWith('/admin')) {
    return <AdminApp />;
  }
  
  // Main chatbot application
  return <App />;
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>,
)
