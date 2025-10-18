import React from 'react'
import ReactDOM from 'react-dom/client'
import { HeroUIProvider } from '@heroui/react'
import { AppRouter } from '@/router'
import { NavigationLoadingProvider } from '@/contexts/NavigationLoadingContext'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { ConnectionProvider } from '@/contexts/ConnectionContext'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <HeroUIProvider>
        <NavigationLoadingProvider>
          <AuthProvider>
            <ConnectionProvider>
              <AppRouter />
            </ConnectionProvider>
          </AuthProvider>
        </NavigationLoadingProvider>
      </HeroUIProvider>
    </ThemeProvider>
  </React.StrictMode>,
)
