@echo off
:: Set root path
set "ROOT_DIR=%~dp0"

echo ################################################
echo #      CoreInventory Local Startup Script      #
echo ################################################

:: Start Backend in a new window
echo [INFO] Starting Backend...
cd /d "%ROOT_DIR%backend"
start "CoreInventory Backend" cmd /k "call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

:: Start Frontend in current window
echo [INFO] Starting Frontend...
cd /d "%ROOT_DIR%frontend"
echo [INFO] Frontend will be available at http://localhost:5173
echo [INFO] Backend API will be available at http://localhost:8000/api/docs
npm run dev
