# Get Started

Step-by-step instructions for running AgricStat Dash on Windows, macOS, and Linux.

See [README.md](README.md) for a project overview, API reference, and configuration details.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Windows Setup](#windows-setup)
- [macOS Setup](#macos-setup)
- [Linux Setup](#linux-setup)
- [Subsequent Runs](#subsequent-runs)
- [Database Initialization](#database-initialization)
- [Verifying the App](#verifying-the-app)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

All platforms require:

| Tool    | Minimum Version | Where to get it                     |
|---------|-----------------|-------------------------------------|
| Python  | 3.11            | https://www.python.org/downloads/   |
| Node.js | 18 (LTS)        | https://nodejs.org/                 |
| Git     | Any             | https://git-scm.com/                |

Verify your installations before proceeding:

```bash
python --version       # or python3 --version on macOS/Linux
node --version
npm --version
git --version
```

---

## Windows Setup

### 1. Clone the repository

Open Command Prompt (`Win + R`, type `cmd`, press Enter):

```cmd
git clone <repository-url>
cd agric-stat-dash
```

### 2. Set up the backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

The terminal should display:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Keep this window open. The backend is now running at `http://localhost:8000`.

### 3. Set up the frontend

Open a second Command Prompt window:

```cmd
cd agric-stat-dash\web
npm install
npm run dev
```

The terminal should display:

```
  VITE v5.x  ready in XXX ms
  Local:   http://localhost:5173/
```

### 4. Open in browser

Navigate to `http://localhost:5173`.

Log in with username `admin` and password `admin123`.

### Windows troubleshooting

**"python is not recognized"**  
Python was not added to PATH during installation. Reinstall Python and check "Add Python to PATH", or add it manually via System Environment Variables.

**"npm is not recognized"**  
Restart Command Prompt after installing Node.js. If it still fails, add the Node.js install directory to your PATH.

**Port 8000 already in use:**

```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Or start the backend on a different port and update `web/.env` accordingly:

```cmd
python -m uvicorn app.main:app --reload --port 8001
```

```env
# web/.env
VITE_API_URL=http://localhost:8001/api
```

---

## macOS Setup

### 1. Clone the repository

Open Terminal (`Cmd + Space`, type "Terminal"):

```bash
git clone <repository-url>
cd agric-stat-dash
```

### 2. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

Keep this terminal open.

### 3. Set up the frontend

Open a second terminal:

```bash
cd agric-stat-dash/web
npm install
npm run dev
```

### 4. Open in browser

Navigate to `http://localhost:5173`. Log in with `admin` / `admin123`.

### macOS troubleshooting

**"python3: command not found"**

```bash
brew install python@3.11
```

If Homebrew is not installed: https://brew.sh/

**Port 8000 already in use:**

```bash
lsof -i :8000
kill -9 <PID>
```

**"permission denied" when activating venv:**

```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

## Linux Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd agric-stat-dash
```

### 2. Install system packages

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
```

For Node.js 18 via NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

Fedora / RHEL:

```bash
sudo dnf install python3.11 python3-pip nodejs npm git
```

### 3. Set up the backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Set up the frontend

Open a second terminal:

```bash
cd agric-stat-dash/web
npm install
npm run dev
```

### 5. Open in browser

Navigate to `http://localhost:5173`. Log in with `admin` / `admin123`.

### Linux troubleshooting

**"python3.11: command not found"**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**Port 8000 already in use:**

```bash
sudo lsof -i :8000
kill -9 <PID>
```

**"npm: command not found" after installing Node.js:**

```bash
# Reload shell or add to PATH manually
source ~/.bashrc
```

---

## Subsequent Runs

After the first-time setup, start the app with:

**Terminal 1 — backend:**

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend:**

```bash
cd web
npm run dev
```

Stop either process with `Ctrl + C`.

---

## Database Initialization

`python init_db.py` creates the database schema and seeds sample data. It is safe to re-run — it skips seeding if data already exists.

Sample data created on first run:

| Type                    | Count |
|-------------------------|-------|
| Products                | 10    |
| Transactions (30 days)  | 90    |
| Demand forecasts        | 20    |
| Inventory recommendations | 5   |

To reset the database to a clean state:

```bash
# From the backend/ directory with venv activated
del agric_stat.db          # Windows
rm agric_stat.db           # macOS / Linux
python init_db.py
```

The database file is `backend/agric_stat.db` (SQLite). It is excluded from version control via `.gitignore`.

---

## Verifying the App

Once both servers are running:

| Check                    | URL / command                           |
|--------------------------|-----------------------------------------|
| Frontend loads           | `http://localhost:5173`                 |
| Backend API docs         | `http://localhost:8000/docs`            |
| Products endpoint        | `http://localhost:8000/api/products`    |
| Auth endpoint            | `POST http://localhost:8000/api/auth/login` |

The dashboard should display KPI cards and charts populated with the seeded sample data.

---

## Troubleshooting

### Pages show "Failed to load" errors

1. Confirm the backend is running (Terminal 1 shows the Uvicorn startup line).
2. Confirm `web/.env` has the correct `VITE_API_URL`.
3. Re-run `python init_db.py` if the database file is missing.

### Frontend loads but shows no data

Open the browser developer console (`F12`). API errors will appear on the Console or Network tab. Common causes:

- CORS: the backend `ALLOWED_ORIGINS` does not include `http://localhost:5173`.
- Wrong port: `VITE_API_URL` points to the wrong backend port.

### Backend crashes on startup

Missing `SECRET_KEY`:

```bash
# Generate a value and add it to backend/.env
python -c "import secrets; print(secrets.token_hex(32))"
```

The backend will refuse to start if `SECRET_KEY` is not set or is left as the placeholder value.

### "Module not found" (Python)

The virtual environment is not activated, or `pip install` was not run.

```bash
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### "Cannot find module" (Node)

`node_modules` is missing or stale.

```bash
cd web
npm install
```

---

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).  
For backend internals, see [backend/README.md](backend/README.md).  
For frontend internals, see [web/README.md](web/README.md).
