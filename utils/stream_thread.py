import cv2
import numpy as np

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

from .ui_utils import show_image


class StreamThread(QThread):
    image_signal = pyqtSignal([np.ndarray, QGraphicsScene, QGraphicsView])
    error_signal = pyqtSignal(str)

    def __init__(self, scene: QGraphicsScene, view: QGraphicsView, video_path: str):
        super(StreamThread, self).__init__()
        self.video_path = video_path
        self.scene = scene
        self.view = view
        self.vidcap = None
        self.running = False

        self.image_signal.connect(show_image)

    def run(self):
        # 在背景執行緒中開啟串流，避免攝影機連不上時整個介面卡住
        self.running = True
        self.vidcap = cv2.VideoCapture(self.video_path)
        if not self.vidcap.isOpened():
            self.vidcap.release()
            if self.running:
                self.error_signal.emit("無法開啟攝影機串流，請確認網路連線與 IP。")
            return

        success, image = self.vidcap.read()
        while success and self.running:
            self.image_signal.emit(image, self.scene, self.view)
            success, image = self.vidcap.read()

        if self.running and not success:
            self.error_signal.emit("串流中斷。")
        self.vidcap.release()

    def stop(self):
        self.running = False
        self.wait()
