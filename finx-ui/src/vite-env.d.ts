/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly NODE_ENV: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_JWT_SECRET: string
  readonly VITE_AUTH_COOKIE_NAME: string
  readonly VITE_DB_CONNECTION_TIMEOUT: string
  readonly VITE_ENABLE_ADMIN_FEATURES: string
  readonly VITE_ENABLE_DEBUG_MODE: string
  readonly VITE_DEFAULT_THEME: string
  readonly VITE_ENABLE_DARK_MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
