import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppRouter } from '@/router'
import { NavigationLoadingProvider } from '@/contexts/NavigationLoadingContext'
import { AuthProvider } from '@/contexts/AuthContext'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <NavigationLoadingProvider>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </NavigationLoadingProvider>
  </React.StrictMode>,
)
