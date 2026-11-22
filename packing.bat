REM Build a single exe into dist\ (run inside the ptz env). Copy config.json next to the exe.
for /f "usebackq delims=" %%i in (`python -c "import sys,os;print(os.path.join(sys.prefix,'Lib','site-packages','wsdl'))"`) do set WSDL=%%i
pyinstaller main.py -n Ptz_Control -i ./icons/video-camera.ico --add-data "./icons;icons" --add-data "%WSDL%;wsdl" --noconsole --onefile
