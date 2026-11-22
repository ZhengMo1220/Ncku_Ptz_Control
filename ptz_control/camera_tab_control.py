# import logging

# logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QWidget, QGraphicsScene, QMessageBox, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from .ptz_control_ui import Ui_ptz_control
from utils.stream_thread import StreamThread
from .ptz_control import ptzControl
from utils.icons_utils import resource_path
from utils.config import load_config, rtsp_url

class PtzTabControl(QWidget):
    def __init__(self):
        super(PtzTabControl, self).__init__()
        self.ui = Ui_ptz_control()
        self.ui.setupUi(self)

        self.config = load_config()
        self._old_threads = []  # 已停止但尚未結束的串流執行緒，避免被回收而崩潰

        self.setup_icons()
        self.init_map()

        self.main_scene = QGraphicsScene()
        self.streaming = False
        self.stream_thread = None
        self.ptz_control = None

        self.bind_ui()

    def setup_icons(self):
        icon_path = resource_path('./icons/up-arrow.png')
        self.ui.move_up_button.setIcon(QIcon(icon_path))

        icon_path = resource_path('./icons/down-arrow.png')
        self.ui.move_down_button.setIcon(QIcon(icon_path))

        icon_path = resource_path('./icons/left-arrow.png')
        self.ui.move_left_button.setIcon(QIcon(icon_path))

        icon_path = resource_path('./icons/right-arrow.png')
        self.ui.move_right_button.setIcon(QIcon(icon_path))

        icon_path = resource_path('./icons/zoom-in.png')
        self.ui.zoom_in_button.setIcon(QIcon(icon_path))

        icon_path = resource_path('./icons/zoom-out.png')
        self.ui.zoom_out_button.setIcon(QIcon(icon_path))


    def init_map(self):
        prefix = self.config["ip_prefix"]
        self.camera_map = {
            **{f"Rot{i:02d}": f"{prefix}{i}" for i in range(1, 21)},
            **{f"Sti{i:02d}": f"{prefix}{i+20}" for i in range(1, 7)},
            **{f"Ptz{i:02d}": f"{prefix}{i+26}" for i in range(1, 9)}
        }

        # Add all keys from camera_map to the combobox
        self.ui.camera_select_combobox.addItems(self.camera_map.keys())

    def bind_ui(self):
        self.ui.connect_camera_button.clicked.connect(self.handle_toggle_stream)

        self.ui.move_left_button.clicked.connect(self.handle_move_left)
        self.ui.move_right_button.clicked.connect(self.handle_move_right)
        self.ui.move_up_button.clicked.connect(self.handle_move_up)
        self.ui.move_down_button.clicked.connect(self.handle_move_down)
        self.ui.zoom_in_button.clicked.connect(self.handle_zoom_in)
        self.ui.zoom_out_button.clicked.connect(self.handle_zoom_out)

        # Add new connection for camera selection change
        self.ui.camera_select_combobox.currentIndexChanged.connect(self.handle_camera_change)

    def handle_camera_change(self):
        if self.streaming:
            self.close_thread(self.stream_thread)
            self.stream_thread = None
            self.ptz_control = None
            self.disable_control_buttons()
            self.start_connect_camera()

    def handle_toggle_stream(self):
        if not self.streaming:
            self.streaming = True
            self.ui.connect_camera_button.setText("停止串流")
            self.start_connect_camera()
        else:
            self.streaming = False
            self.ui.connect_camera_button.setText("讀取串流")
            self.disable_control_buttons()
            self.close_thread(self.stream_thread)
            self.stream_thread = None
            self.ptz_control = None

    def close_thread(self, thread):
        """停止串流執行緒但不阻塞介面（攝影機連線中時 wait 可能要等數十秒）。"""
        if thread is None:
            return
        thread.running = False
        try:
            thread.image_signal.disconnect()
            thread.error_signal.disconnect()
        except TypeError:
            pass
        self._old_threads.append(thread)
        thread.finished.connect(lambda t=thread: self._old_threads.remove(t) if t in self._old_threads else None)

    def handle_stream_error(self, message):
        if self.streaming:
            self.handle_toggle_stream()  # 回到未串流狀態
        QMessageBox.warning(self, "串流錯誤", message)

    def stop_all_threads(self):
        """關閉視窗時呼叫，確保所有執行緒結束。"""
        self.close_thread(self.stream_thread)
        self.stream_thread = None
        for t in list(self._old_threads):
            t.wait(3000)

    def start_connect_camera(self):
        print("reconnecting")
        camera_display_name = self.ui.camera_select_combobox.currentText()
        try:
            camera_ip = self.camera_map[camera_display_name]
        except KeyError:
            # print(f"no camera named {camera_display_name}!")
            self.stream_thread = None
            self.ptz_control = None
            return
        
        self.stream_thread = StreamThread(self.main_scene, self.ui.main_view, rtsp_url(self.config, camera_ip))
        self.stream_thread.error_signal.connect(self.handle_stream_error)
        self.stream_thread.start()

        controllable = (camera_display_name.startswith("Ptz")
                        and camera_display_name not in self.config["no_control_cameras"])
        if not controllable:
            self.disable_control_buttons()
            return

        # 連線 ONVIF（PTZ 控制）；失敗時只停用控制按鈕，不讓程式崩潰
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.ptz_control = ptzControl(camera_ip, self.config["username"], self.config["password"],
                                          port=self.config["onvif_port"])
            self.enable_control_buttons()
        except Exception as e:
            self.ptz_control = None
            self.disable_control_buttons()
            QMessageBox.warning(self, "PTZ 控制連線失敗",
                                f"無法連線到 {camera_display_name} ({camera_ip}) 的 PTZ 控制：\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def enable_control_buttons(self):
        self.ui.move_left_button.setEnabled(True)
        self.ui.move_right_button.setEnabled(True)
        self.ui.move_up_button.setEnabled(True)
        self.ui.move_down_button.setEnabled(True)
        self.ui.zoom_in_button.setEnabled(True)
        self.ui.zoom_out_button.setEnabled(True)

    def disable_control_buttons(self):
        self.ui.move_left_button.setEnabled(False)
        self.ui.move_right_button.setEnabled(False)
        self.ui.move_up_button.setEnabled(False)
        self.ui.move_down_button.setEnabled(False)
        self.ui.zoom_in_button.setEnabled(False)
        self.ui.zoom_out_button.setEnabled(False)

    def _safe_ptz(self, action):
        if self.ptz_control is None:
            return
        try:
            getattr(self.ptz_control, action)()
        except Exception as e:
            QMessageBox.warning(self, "PTZ 控制錯誤", f"{action} 失敗：{e}")

    def handle_move_up(self):
        self._safe_ptz("move_down")

    def handle_move_down(self):
        self._safe_ptz("move_up")

    def handle_move_left(self):
        self._safe_ptz("move_left")

    def handle_move_right(self):
        self._safe_ptz("move_right")

    def handle_zoom_in(self):
        self._safe_ptz("zoom_in")

    def handle_zoom_out(self):
        self._safe_ptz("zoom_out")