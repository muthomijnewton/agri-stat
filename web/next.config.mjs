import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
export default {
  devIndicators: false,
  turbopack: { root: dirname(fileURLToPath(import.meta.url)) },
  env: { NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || process.env.VITE_API_URL || 'http://localhost:8001/api' },
}
