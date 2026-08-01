@echo off
title MCP Knowledge Assistant - Launcher
cd /d "%~dp0"

REM Make Python output UTF-8 (inherited by the server windows).
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo ============================================
echo   MCP Knowledge Assistant - starting up
echo ============================================
echo.

REM --- 0. Clean restart: stop any old servers still holding the ports, so the
REM     freshly launched ones always run the current code (never a stale build).
echo [0/4] Clearing any old servers on ports 3000/8000/8001...
for %%P in (3000 8000 8001) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%P ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
  )
)

REM --- 1. Ensure Docker engine + Qdrant container (handled by PowerShell) ---
echo [1/4] Checking Docker and Qdrant...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "if (-not (docker ps 2>$null)) { Write-Host '      Docker not running - launching Docker Desktop...'; Start-Process 'C:\Users\deepa\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe'; $n=0; while ($true) { docker ps *> $null 2>&1; if ($LASTEXITCODE -eq 0) { break }; if ($n -ge 40) { Write-Host '      ERROR: Docker did not start in time.'; exit 1 }; Start-Sleep 3; $n++ } }; docker start qdrant *> $null 2>&1; if ($LASTEXITCODE -ne 0) { Write-Host '      Creating Qdrant container...'; docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant }; Write-Host '      Qdrant is up.'"
if errorlevel 1 (
  echo.
  echo Could not start Docker/Qdrant. Open Docker Desktop manually and retry.
  pause
  exit /b 1
)

REM --- 2. MCP server (tool layer) on 8001 ---
echo [2/4] Starting MCP server on http://localhost:8001 ...
start "MCP Server (8001)" /D "%~dp0backend" cmd /k "..\venv\Scripts\python.exe -m app.mcp.server"

REM --- 3. Backend API on 8000 ---
echo [3/4] Starting Backend API on http://localhost:8000 ...
start "Backend API (8000)" /D "%~dp0backend" cmd /k "..\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

REM --- 4. Frontend (React) on 3000 ---
echo [4/4] Starting Frontend on http://localhost:3000 ...
start "Frontend (3000)" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo Waiting for servers to warm up...
timeout /t 12 /nobreak >nul

echo Opening http://localhost:3000 ...
start "" http://localhost:3000

echo.
echo ============================================
echo   All services launched in separate windows.
echo   Close those windows (or run stop_app.bat)
echo   to shut everything down.
echo.
echo   Tip: if the UI ever looks out of date, press
echo   Ctrl+Shift+R in the browser for a hard refresh.
echo ============================================
echo.
echo This launcher window can be closed.
pause
