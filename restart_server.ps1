# Restart Daphne Server Script
# This will restart the server to pick up new URL configurations

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Restarting Daphne Server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

# Stop existing daphne process
Write-Host "`n1. Stopping existing Daphne process..." -ForegroundColor Cyan
$daphneProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*daphne*" }

if ($daphneProcesses) {
    foreach ($proc in $daphneProcesses) {
        Write-Host "   Stopping process ID: $($proc.Id)" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force
    }
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Process stopped" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No Daphne process found" -ForegroundColor Gray
}

# Start daphne
Write-Host "`n2. Starting Daphne server on port 8002..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; daphne -b 0.0.0.0 -p 8002 core.asgi:application"

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "✅ Server restarted successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "`nServer running at: http://localhost:8002" -ForegroundColor White
Write-Host "Dashboard API: http://localhost:8002/api/hume-twilio/dashboard/" -ForegroundColor White
Write-Host "`nPress Ctrl+C in the new window to stop the server." -ForegroundColor Gray
