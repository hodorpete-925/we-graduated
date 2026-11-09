@echo off
rem One-step We Graduated refresh: pulls Yahoo, rebuilds the site, publishes to GitHub.
rem Double-click it, or run "refresh" from this folder. Extra options pass through,
rem e.g.  refresh --no-publish   or   refresh --site-only
cd /d "%~dp0"
"..\Fantasy Football API Work\venv\Scripts\python.exe" refresh.py %*
echo.
pause
