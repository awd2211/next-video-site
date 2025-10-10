/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_BASE_URL?: string
  // 添加更多环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
