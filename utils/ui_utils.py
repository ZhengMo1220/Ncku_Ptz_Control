import os
import glob
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cv2
import numpy as np

class DataType(Enum):
    DEFAULT = {"name": "default", "tips": "", "filter": ""}
    IMAGE = {"name": "image", "tips": "",
             "filter": "Image files (*.jpeg *.png *.tiff *.psd *.pdf *.eps *.gif *.jpg)"}
    VIDEO = {"name": "video", "tips": "",
             "filter": "Video files ( *.WEBM *.MPG *.MP2 *.MPEG *.MPE *.MPV *.OGG *.MP4 *.M4P *.M4V *.AVI *.WMV *.MOV *.QT *.FLV *.SWF *.MKV)"}
    CSV = {"name": "csv", "tips": "",
           "filter": "Video files (*.csv)"}
    FOLDER = {"name": "folder", "tips": "", "filter": ""}

def load_data(dir_path="../../Db", value_filter=None, mode=DataType.DEFAULT):
    data_path = None
    if mode == DataType.FOLDER:
        data_path = QFileDialog.getExistingDirectory(
            None, mode.value['tips'], dir_path)
    else:
        name_filter = mode.value['filter'] if value_filter == None else value_filter
        data_path, _ = QFileDialog.getOpenFileName(
            None, mode.value['tips'], dir_path, name_filter)

    return data_path      
        
def load_image():
    image_path = load_data(mode=DataType.IMAGE)       
    # no video found
    if image_path == "":
        return
    
    image_name = os.path.basename(image_path)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    return image_name, image

def load_images(folder_path):
    image_list = []

    images = glob.glob(folder_path + '/*.JPG')
    for filename in images:
        image = cv2.imread(filename)
        image_list.append(image)
    
    return image_list

def show_image(image: np.ndarray, scene: QGraphicsScene, GraphicsView: QGraphicsView):
    if image is None:
        return
    
    scene.clear()
    image = image.copy()

    # Resize the image to fit the GraphicsView
    image = cv2.resize(image, (GraphicsView.width(), GraphicsView.height()), interpolation=cv2.INTER_AREA)

    # Check if the image is grayscale (single channel)
    if len(image.shape) == 2:
        # Create a grayscale QImage
        qImg = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)
    else:
        # Convert the image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qImg = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)

    scene.clear()
    GraphicsView.setScene(scene)
    scene.addPixmap(QPixmap.fromImage(qImg))
    
def load_video_into_buffer(input_video_path):
    video_images = []
    vidcap = cv2.VideoCapture(input_video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    success, image = vidcap.read()
    count = 0
    while success:
        video_images.append(image)
        count += 1
        success, image = vidcap.read()
    vidcap.release()
    # set image count labels
    return video_images, fps, count

