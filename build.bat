@echo off
echo ===========================================
echo    Screenshot Paster Executable Builder
echo ===========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please make sure Python is installed and in your PATH.
    pause
    exit /b 1
)

REM Run the build script
echo Running build script...
python build_exe.py

echo.
echo Build process completed!
echo Check the 'dist' folder for your executable.
echo.
pause

