/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** "true" shows the "Probar la demo" button on the login page. */
  readonly VITE_DEMO_ENABLED?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
