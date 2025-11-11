@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                 🚀 AUTO START - HUMAN-LIKE CONVERSATION SYSTEM              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 CHECKLIST:
echo.
echo [1] Have you configured HumeAI Dashboard?
echo     URL: https://platform.hume.ai/
echo     Config: 13624648-658a-49b1-81cb-a0f2e2b05de5
echo.
echo [2] Did you enable TRANSCRIPTION in HumeAI Dashboard?
echo     This is CRITICAL - without this you get empty transcripts!
echo.
echo [3] Did you set TURN-TAKING to BALANCED mode (800ms)?
echo     This makes agent LISTEN before responding!
echo.
set /p ready="Press Y to start server (N to see configuration guide): "
if /i "%ready%" NEQ "Y" (
    echo.
    echo Opening configuration guide...
    python APPLY_HUME_SETTINGS.py
    pause
    exit /b
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🛑 Stopping existing servers...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
powershell -Command "Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force"
timeout /t 2 /nobreak > nul

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 Starting Django with HUMAN-LIKE AI Configuration...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ HumeAI Config: 13624648-658a-49b1-81cb-a0f2e2b05de5
echo ✅ Mode: BALANCED (Agent listens before responding)
echo ✅ Transcription: ENABLED (Text saving enabled)
echo ✅ Greeting: ENABLED (Natural greeting)
echo ✅ Port: 8002
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

call venv\Scripts\activate.bat
daphne -b 0.0.0.0 -p 8002 core.asgi:application
