'use client'
import dynamic from 'next/dynamic'
// Keep existing browser-only authentication and routes during the Next.js transition.
const App = dynamic(() => import('../App'), { ssr: false, loading: () => <main className="startup" role="status">Opening AgriStat…</main> })
export default App
