call conda.bat activate ptz
if errorlevel 1 (
    echo [ERROR] conda env "ptz" not found. Please run install.bat first.
    pause
    exit /b 1
)
cd /d %~dp0
python main.py
if errorlevel 1 pause
