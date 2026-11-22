call conda.bat create python=3.9 -n ptz -y
call conda.bat activate ptz

pip install -r requirements.txt

if not exist config.json copy config.example.json config.json
echo.
echo Done. Please edit config.json (camera username / password), then run start.bat
pause
