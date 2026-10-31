# Deployment & Setup Guide (Windows 10/11)

## 1. System Prerequisites
- **Operating System**: Windows 10 or Windows 11 (64-bit).
- **Python**: Python 3.12+ (CPython 3.12 recommended for binary wheel compatibility).
- **Node.js**: Node.js v18+ (verified with v22).
- **FFmpeg**: Installed and accessible in Windows `PATH` (verified with FFmpeg 8.1.1).
- **CapCut Desktop** (Optional for editing): Installed at `%LOCALAPPDATA%\CapCut`.

---

## 2. Fast Installation using `uv` & `npm`

### Step 1: Clone and Enter Directory
```powershell
cd d:\HOCTAP\latvat\crawlTHREAD
```

### Step 2: Set Up Python Backend Environment
```powershell
# Create Python 3.12 virtual environment
uv venv .venv --python 3.12

# Install backend dependencies
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

### Step 3: Set Up React Frontend Environment
```powershell
cd frontend
npm install
npm run build
cd ..
```

### Step 4: Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

---

## 3. Starting the Application

Use the included PowerShell start script `run_studio.ps1`:
```powershell
.\run_studio.ps1
```

Or run manually:
- Backend:
  ```powershell
  .\.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- Frontend:
  ```powershell
  cd frontend
  npm run dev
  ```

Open browser at: `http://localhost:5173` (or `http://localhost:8000` when served statically).
