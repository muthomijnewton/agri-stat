# 🚀 Get Started Guide

Complete step-by-step instructions for running the Agricultural Statistics Dashboard on Windows, macOS, and Linux.

**Table of Contents:**
- [Windows Setup](#-windows)
- [macOS Setup](#-macos)
- [Linux Setup](#-linux)
- [Running the App](#-running-the-app)
- [Database Setup](#-database-initialization)
- [Troubleshooting](#-troubleshooting)

---

## 💻 Windows

### Prerequisites
1. **Python 3.13+**
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt and type `python --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Choose "LTS" version
   - Verify: Open Command Prompt and type `node --version` and `npm --version`

3. **Git**
   - Download: https://git-scm.com/
   - Verify: Open Command Prompt and type `git --version`

### Step 1: Clone the Project

```bash
# Open Command Prompt (Win + R, type cmd, press Enter)
git clone <your-repository-url>
cd agric-stat-dash
```

### Step 2: Set Up Backend

**Open Command Prompt and run:**

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) at the start of the command line

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python init_db.py

# Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Backend is ready!** → http://localhost:8000/docs

**Keep this Command Prompt window OPEN** (don't close it)

### Step 3: Set Up Frontend

**Open a NEW Command Prompt and run:**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start frontend development server
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in XXX ms
➜  Local:   http://localhost:3001/
```

### Step 4: Open In Browser

**Open your web browser and go to:**
```
http://localhost:3001
```

✅ **App is running!** 🎉

You should see:
- Dashboard with statistics
- Navigation menu with: Home, Products, Transactions, Forecasts, Recommendations
- Charts and data tables with sample data

### Troubleshooting for Windows

**"Python is not recognized"**
- Python not added to PATH
- Fix: Reinstall Python and check "Add Python to PATH"

**"npm is not recognized"**
- Node.js not added to PATH
- Fix: Restart Command Prompt after Node.js installation
- Or add manually: Search "Environment Variables" → Edit System Variables → Add Node.js path

**"Port 8000 is already in use"**
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with Process ID)
taskkill /PID XXXX /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

**"cmd.exe: The terminalprogram is not found"**
- Close and reopen Command Prompt after installations

**Module not found errors**
```bash
# Make sure virtual environment is activated (check for (venv) in command line)
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🍎 macOS

### Prerequisites

1. **Python 3.13+**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.13
   
   # Verify
   python3 --version
   ```
   
   Or download: https://www.python.org/downloads/

2. **Node.js 18+**
   ```bash
   # Using Homebrew (recommended)
   brew install node
   
   # Verify
   node --version
   npm --version
   ```
   
   Or download: https://nodejs.org/

3. **Git**
   ```bash
   # Usually pre-installed on macOS
   git --version
   
   # If not installed
   brew install git
   ```

### Step 1: Clone the Project

```bash
# Open Terminal (Command + Space, type "Terminal", press Enter)
git clone <your-repository-url>
cd agric-stat-dash
```

### Step 2: Set Up Backend

**In Terminal, run:**

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) at the start of the terminal line

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python init_db.py

# Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Backend is ready!** → http://localhost:8000/docs

**Keep this Terminal window OPEN** (don't close it)

### Step 3: Set Up Frontend

**Open a NEW Terminal window and run:**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start frontend development server
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in XXX ms
➜  Local:   http://localhost:3001/
```

### Step 4: Open In Browser

**Open your web browser and go to:**
```
http://localhost:3001
```

✅ **App is running!** 🎉

You should see:
- Dashboard with statistics
- Navigation menu with: Home, Products, Transactions, Forecasts, Recommendations
- Charts and data tables with sample data

### Troubleshooting for macOS

**"python3: command not found"**
```bash
# Install via Homebrew
brew install python@3.13
brew link python@3.13

# Verify
python3 --version
```

**"Port 8000 already in use"**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace XXXX with Process ID)
kill -9 XXXX

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

**"Permission denied" errors**
```bash
# Make sure virtual environment is activated (check for (venv) in terminal)
# Try running with python (not python3) after activating venv
```

**Module not found**
```bash
# Ensure you're in venv (should see (venv) in terminal)
# Reinstall:
pip install --upgrade pip
pip install -r requirements.txt
```

**"npm: command not found"**
```bash
# Install Node.js
brew install node

# Verify
node --version
npm --version
```

---

## 🐧 Linux

### Prerequisites

1. **Python 3.13+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.13 python3.13-venv python3-pip
   
   # Fedora/RHEL
   sudo dnf install python3.13 python3-pip
   
   # Verify
   python3.13 --version
   ```

2. **Node.js 18+**
   ```bash
   # Using NodeSource repository (Ubuntu/Debian)
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install nodejs
   
   # Fedora/RHEL
   sudo dnf install nodejs npm
   
   # Verify
   node --version
   npm --version
   ```

3. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # Fedora/RHEL
   sudo dnf install git
   
   # Verify
   git --version
   ```

### Step 1: Clone the Project

```bash
# Open Terminal
git clone <your-repository-url>
cd agric-stat-dash
```

### Step 2: Set Up Backend

**In Terminal, run:**

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) at the start of the terminal line

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python init_db.py

# Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Backend is ready!** → http://localhost:8000/docs

**Keep this Terminal window OPEN** (don't close it)

### Step 3: Set Up Frontend

**Open a NEW Terminal window and run:**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start frontend development server
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in XXX ms
➜  Local:   http://localhost:3001/
```

### Step 4: Open In Browser

**Open your web browser and go to:**
```
http://localhost:3001
```

✅ **App is running!** 🎉

You should see:
- Dashboard with statistics
- Navigation menu with: Home, Products, Transactions, Forecasts, Recommendations
- Charts and data tables with sample data

### Troubleshooting for Linux

**"python3.13: command not found"**
```bash
# Update and reinstall
sudo apt update
sudo apt install python3.13 python3.13-venv

# Verify
python3.13 --version
```

**"Port 8000 already in use"**
```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process (replace XXXX with Process ID)
kill -9 XXXX

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

**Permission denied**
```bash
# Make sure virtual environment is activated (check for (venv) in terminal)
# Don't use sudo for pip commands inside venv
```

**"npm: command not found"**
```bash
# Reinstall Node.js
sudo apt update
sudo apt install nodejs npm

# Or use NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

---

## ▶️ Running the App

### Quick Start (After First Setup)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate    # (venv\Scripts\activate on Windows)
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Browser:**
```
http://localhost:3001
```

### Stop the App

- **Backend:** Press `Ctrl+C` in Terminal 1
- **Frontend:** Press `Ctrl+C` in Terminal 2
- To close completely, close both Terminal windows

### Restart the App

- Just repeat the "Quick Start" steps above

---

## 📊 Database Initialization

### First Time Setup

When you first run `python init_db.py`, it creates:

✅ **10 Products**
- Tomatoes, Maize, Beans, Potatoes, Carrots, Cabbage, Onions, Wheat, Lettuce, Peppers

✅ **90 Sample Transactions**
- 30 days of realistic sales data across all products

✅ **20 Demand Forecasts**
- AI predictions for each product over 10 days
- Includes confidence intervals

✅ **5 Inventory Recommendations**
- Smart reorder suggestions with different statuses
- Based on historical data

### Reset Database (Start Fresh)

```bash
# In backend folder
python init_db.py --reset
```

This will:
1. Delete existing database
2. Create fresh tables
3. Add sample data

### Database Location

The database file is created at:
- **Location:** `backend/agric_stat.db` (SQLite file)
- **Size:** ~200KB after initialization
- **Can be deleted:** Yes, just run `init_db.py` again to recreate

---

## 🔍 How to Use the App

### Navigation

**Menu Items:**
- **Home** - Dashboard with overview and charts
- **Products** - Manage agricultural products
- **Transactions** - View sales history
- **Forecasts** - AI demand predictions
- **Recommendations** - Inventory optimization suggestions

### Dashboard
- View key statistics at a glance
- See recent transactions
- Check demand trends
- Monitor forecast accuracy

### Products Page
- View all products in a table
- Click "Add Product" to create new ones
- See product categories and pricing
- Delete products as needed

### Transactions Page
- Browse all sales records
- View product name, quantity, price, date
- Track total revenue
- Filter by date range

### Forecasts Page
- See AI predictions by product
- View predicted demand with confidence bounds
- Check forecast accuracy percentage
- Understand forecasting timeline

### Recommendations Page
- Get smart inventory suggestions
- View recommended vs current stock
- Approve or implement recommendations
- Track inventory optimization status

---

## 🔗 API Access

### API Documentation (Interactive)

When backend is running, visit:
```
http://localhost:8000/docs
```

This shows:
- All available endpoints
- Request/response formats
- Try endpoints directly
- See real data from database

### Example API Calls

**Get All Products:**
```bash
curl http://localhost:8000/api/products/
```

**Get Transactions:**
```bash
curl http://localhost:8000/api/transactions/
```

**Get Forecasts:**
```bash
curl http://localhost:8000/api/forecasts/
```

**Get Recommendations:**
```bash
curl http://localhost:8000/api/recommendations/
```

---

## 🆘 Troubleshooting

### "Failed to Load" Errors in Browser

**Error:** Page shows "Failed to load products" or similar

**Causes:**
1. Backend server not running
2. Port 3001 can't reach port 8000
3. Database not initialized

**Fix:**
```bash
# 1. Check backend is running
# Terminal 1 should show: "Uvicorn running on http://0.0.0.0:8000"

# 2. Initialize database
cd backend
python init_db.py

# 3. Restart both servers
# Press Ctrl+C on both terminals
# Rerun Quick Start commands above
```

### "Connection Refused" or "Cannot Connect"

**Error:** Browser shows ERR_CONNECTION_REFUSED

**Fix:**
```bash
# 1. Verify backend is running (check Terminal 1)
# 2. Check port 8000 is not blocked
# 3. Try different port:
python -m uvicorn app.main:app --reload --port 8001
# Then access: http://localhost:3001 (frontend auto-discovers backend)
```

### Blank Page in Browser

**Error:** Page loads but nothing displays

**Fix:**
```bash
# 1. Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (macOS)
# 2. Check browser console (F12) for errors
# 3. Clear browser cache and try again
# 4. Restart frontend: Ctrl+C then npm run dev
```

### Python/Node Version Issues

**Error:** "Python 3.13 required" or "Node 18 required"

**Fix:**
```bash
# Check your versions
python --version
node --version

# Update if needed:
# Python: https://www.python.org/downloads/
# Node: https://nodejs.org/
```

### Modules Not Found

**Error:** "ModuleNotFoundError" or "Cannot find module"

**Fix:**
```bash
# Backend
cd backend
source venv/bin/activate    # (venv\Scripts\activate on Windows)
pip install -r requirements.txt

# Frontend
cd frontend
npm cache clean --force
npm install
```

### Port Already in Use

**Error:** "Address already in use" or "Port 8000 in use"

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID XXXX /F
```

**macOS/Linux:**
```bash
lsof -i :8000
kill -9 XXXX
```

Or use different port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### Database Errors

**Error:** "Database is locked" or similar

**Fix:**
```bash
# 1. Stop backend (Ctrl+C)
# 2. Delete database
rm backend/agric_stat.db

# 3. Reinitialize
cd backend
python init_db.py

# 4. Restart backend
python -m uvicorn app.main:app --reload --port 8000
```

### Still Having Issues?

**Debug Steps:**

1. **Check All Prerequisites**
   ```bash
   python --version   # Should be 3.13+
   node --version     # Should be 18+
   npm --version      # Should be 9+
   git --version      # Should be installed
   ```

2. **Check Terminals Running**
   - Terminal 1: Backend (port 8000)
   - Terminal 2: Frontend (port 3001)
   - Both should show "running" messages

3. **Check Environment Files**
   - Frontend `.env` (should exist in frontend folder)
   - Backend `.env` (should exist in project root)

4. **Manual Test API**
   ```bash
   # Test backend is responding
   curl http://localhost:8000/api/products/
   
   # Should return JSON with products
   ```

5. **Browser Console**
   - Open browser (F12)
   - Check Console tab for error messages
   - Note the exact error and search for solution

---

## 📞 Getting Help

If you get stuck:

1. **Read the error** - Usually tells you exactly what's wrong
2. **Check Troubleshooting** section above
3. **Check Prerequisites** - Make sure all software is installed
4. **Restart Services** - Stop and restart both terminal windows
5. **Check Documentation** - See README.md for more info

---

## 🎯 Next Steps After Setup

✅ **You've successfully set up the app!**

Now:
1. Explore the Dashboard and see sample data
2. Click through each page (Products, Transactions, Forecasts, Recommendations)
3. Try adding a new product
4. Check the API documentation at http://localhost:8000/docs
5. Review the code in `frontend/src` and `backend/app`

---

**Happy developing! 🚀**

For more information, see [README.md](README.md)
