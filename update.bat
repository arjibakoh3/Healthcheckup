@echo off
setlocal
cd /d "%~dp0"

git add .
git commit -m "update"
git push

echo.
echo Done. If there were no changes, commit may be skipped.
pause
