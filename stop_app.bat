@echo off
title MCP Knowledge Assistant - Stop
echo Stopping app services (ports 3000, 8000, 8001)...

for %%P in (3000 8000 8001) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%P ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
  )
)

echo Stopping Qdrant container...
docker stop qdrant >nul 2>&1

echo.
echo All services stopped.
pause
