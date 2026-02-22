# AdForge — start backend + frontend in two windows
$root = $PSScriptRoot

# Backend
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$root'; Write-Host '=== BACKEND ===' -ForegroundColor Cyan; python -m uvicorn backend.main:app --reload --port 8000"
)

# Frontend
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$root\frontend-react'; Write-Host '=== FRONTEND ===' -ForegroundColor Magenta; npm run dev"
)

Write-Host "Both servers starting..." -ForegroundColor Green
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend -> http://localhost:3000" -ForegroundColor Magenta
Write-Host "Open http://localhost:3000 in your browser." -ForegroundColor Yellow
