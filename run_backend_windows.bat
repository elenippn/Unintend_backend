@echo off
REM Convenience wrapper (avoids PowerShell execution policy issues)
powershell -ExecutionPolicy Bypass -File "%~dp0run_backend_windows.ps1"
