# Start AgriStat locally

## Existing installation

```bash
cd ~/agri-stat
sudo docker compose --env-file infra/.env -f infra/compose.yaml up --build -d
sudo docker compose --env-file infra/.env -f infra/compose.yaml ps -a
cd web
npm ci
npm run build
npm start
```

Open [AgriStat](http://localhost:5173). Keep the web terminal running. Use your existing account. The API documentation is at [localhost:8001/docs](http://localhost:8001/docs). `localhost` means this computer, not a public website.

## New installation

Install Git, Docker Engine with Compose, Node.js 22 and npm. Clone the repository once:

```bash
git clone https://github.com/muthomijnewton/agri-stat.git
cd agri-stat
cp infra/.env.example infra/.env
cp web/.env.example web/.env.local
```

Generate two independent random hexadecimal strings, for example by running `openssl rand -hex 32` twice. Edit `infra/.env`: use one as `POSTGRES_PASSWORD` and the other as `SECRET_KEY`. Do not reuse placeholder values or publish this file. Set the web API URL to `http://localhost:8001/api`.

Start the infrastructure using the existing-installation commands above. To initialize the local Kenya road service, run `sudo bash infra/start_local_overpass.sh` from the repository root. See [Phase 1](docs/PHASE1.md) for download progress, initialization and readiness checks. Download completion is not import completion.

The initializer creates a development administrator if one does not exist; see [Phase 1](docs/PHASE1.md) for local credentials. Replace development credentials before any public deployment. Sample business-data seeding is disabled in Compose.

## First real records

1. Add your actual farm location and produce catalog entries.
2. Record received harvest batches with quantities, dates and known expiry.
3. Record each actual sale in Stock & sales.
4. Confirm completed daily sales totals, or import genuine historical totals as an administrator.
5. Validate a forecast after enough consecutive history exists. Review recommendations rather than treating them as automatic orders.

Public market prices cannot replace your farm's private sales history. See [the operator guide](docs/HOW_AGRISTAT_WORKS.md) and [Phase 3 guide](docs/PHASE3.md).

## Development mode

Run `npm run dev` from `web/` instead of the build/start pair. Only one web server can bind port 5173. Backend source changes need an image rebuild; frontend source changes appear automatically in development mode.
