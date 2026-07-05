@echo off
echo ===================================================
echo   Surakshify Setup ^& Git Initialization Script
echo ===================================================
echo.

rem 1. Create docs folder
if not exist docs (
    echo Creating docs directory...
    mkdir docs
)

rem 2. Copy generated architecture diagram from artifact directory
echo Copying generated architecture diagram...
copy "C:\Users\Admin\.gemini\antigravity-ide\brain\f7d0b5ab-caaa-4226-83d8-5dea72062741\architecture_diagram_1783268458329.png" "docs\architecture-diagram.png" /Y

echo.
rem 3. Initialize git repository
echo Initializing Git repository...
git init

echo Adding files to git...
git add .

echo Committing initial structure...
git commit -m "Initial commit: Surakshify - GFF 2026 SBI Hackathon submission"

echo Setting branch to main...
git branch -M main

echo.
echo ===================================================
echo   Git initialized locally and diagram copied!
echo ===================================================
echo.
echo To link and push to your remote GitHub repository, run:
echo   git remote add origin https://github.com/shuvetajovia/surakshify.git
echo   git push -u origin main
echo.
pause
