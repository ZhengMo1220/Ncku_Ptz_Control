# Standard Library
import sys
import traceback
# import logging

# logging.basicConfig(filename='processing.log', 
#                     format='%(asctime)s %(levelname)-8s %(message)s',
#                     level=logging.INFO,
#                     datefmt='%Y-%m-%d %H:%M:%S')
# logger = logging.getLogger(__name__)

# Addon Library
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon

# Custom Made Python Code
from main_window_ui import Ui_MainWindow
from ptz_control.camera_tab_control import PtzTabControl
from utils.icons_utils import resource_path

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_tabs()

        self.set_window_icon()

    def init_tabs(self):
        self.ptz_tab = PtzTabControl()
        self.ui.Two_d_Tab.addTab(self.ptz_tab, "單隻攝影機")

    def set_window_icon(self):
        icon_path = resource_path('./icons/video-camera.png')
        self.setWindowIcon(QIcon(icon_path))

    def closeEvent(self, event):
        self.ptz_tab.stop_all_threads()
        super(Main, self).closeEvent(event)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        window = Main()
    except (FileNotFoundError, ValueError) as e:
        QMessageBox.critical(None, "缺少設定檔", str(e))
        sys.exit(1)
    window.show()
    sys.exit(app.exec_())