# AgriStat web application

Next.js 16 hosts a React 18 client workspace. React Router 7 remains the client routing bridge during the incremental migration. FastAPI owns authentication and business rules; PostgreSQL owns business records.

## Run

```bash
npm ci
npm run dev
```

For the production build, use `npm run build` followed by `npm start`. Both modes serve port 5173 and must not run together. Set `NEXT_PUBLIC_API_URL=http://localhost:8001/api` in ignored `.env.local` before building. The former `VITE_API_URL` remains a temporary compatibility fallback.

## Structure

- `src/app/`: Next.js layout, catch-all entry and client loader.
- `src/App.jsx`: authenticated shell, navigation and client routes.
- `src/screens/`: overview, operations, planning, maps, import and retained earlier screens.
- `src/components/charts/ForecastBand.jsx`: predictive band, point values and exact-value table.
- `src/components/maps/RouteMap.jsx`: Leaflet map with OSM attribution and weather layers.
- `src/services/`: API client and shared record/formatting helpers.
- `src/css/workspace.css`: responsive workspace and high-contrast palette.

Run `npm test` for core contrast checks and `npm run build` for production compilation. These checks do not replace full accessibility or end-to-end audits. React 18 support is deprecated by the installed Next.js release; upgrade it before a future Next.js 17 migration.

See [Phase 3](../docs/PHASE3.md) for workflows, screenshots, verification and known boundaries.
