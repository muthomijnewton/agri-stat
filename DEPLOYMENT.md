# Deployment and release verification

The verified deployment is local Docker infrastructure plus a Next.js web server. This is not yet a publicly hosted production service.

## Apply a release

From the repository root:

```bash
sudo docker compose --env-file infra/.env -f infra/compose.yaml up --build -d
sudo docker compose --env-file infra/.env -f infra/compose.yaml ps -a
```

`migrate` should finish with exit code 0. PostgreSQL, Redis, API and Overpass should become healthy. Workers and Beat should stay running. An Overpass first import takes longer than a normal restart. Inspect service logs when health checks fail.

Build the web app with the intended API address already set in ignored `web/.env.local`:

```bash
cd web
npm ci
npm test
npm run build
npm start
```

The browser API address is embedded at build time. Changing it requires a new build. Use a Node server for this Next.js application; the old Vite `dist/` static-host instructions no longer apply.

## Verify the release

- Sign in at [localhost:5173](http://localhost:5173) and check Overview, Stock & sales, Demand planning, Roads & weather, Market prices and the administrator import screen.
- Check that real data remains present and empty farm histories stay empty.
- Confirm the API schema contains `/api/v1/dashboard`, `/api/v1/map-data` and `/api/v1/admin/import-csv`.
- Run backend and PostgreSQL tests in isolated test schemas. Never insert demonstration records into operational farm tables for screenshots.
- For a full local road verification, follow [Phase 1](docs/PHASE1.md). A healthy container alone is not proof of successful route analysis.

## Persistence and startup

Named volumes retain PostgreSQL, Redis and Overpass data when application images are rebuilt. Do not run `docker compose down -v` for a normal update. Back up PostgreSQL before structural changes.

Infrastructure services use `restart: unless-stopped`; migration is a one-shot job. Docker itself must be enabled at system startup. The separately launched web server must also be started; it is not automatically managed by Compose.

Secrets belong in ignored environment files, never Git. Compose binds published ports to loopback. Public HTTPS, credential hardening, backups with recovery drills, database row-level security and monitoring require the production-hardening phase before broader deployment.
