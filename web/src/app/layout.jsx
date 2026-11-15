import '../css/index.css'
export const metadata = { title: 'AgriStat · Farm intelligence', description: 'Farm stock, sales, demand and road intelligence.' }
export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>
}
