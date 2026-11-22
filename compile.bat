pyuic5 -x main_window.ui -o main_window_ui.py --import-from=PyQt5
cd ptz_control
pyuic5 -x ptz_control.ui -o ptz_control_ui.py --import-from=PyQt5
cd ..