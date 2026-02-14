@echo off
echo ===================================================
echo  PUSHING LATEST CODE TO GITHUB
echo ===================================================
cd /d "%~dp0"

echo 1. Ensuring we are on main branch...
git checkout -B main

echo 2. Adding all files...
git add .

echo 3. Committing changes...
git commit -m "Update: Latest code for deployment"

echo 4. Pushing to GitHub...
git push origin main --force

echo.
echo ===================================================
echo  DONE! Your code is now on GitHub.
echo ===================================================
pause