from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent
import sys
import os

class ImageSet:
    def __init__(self,folder,scale_factor):
        self.images = []
        self.index = 0
        self.folder = folder
        for filename in os.listdir(folder):
            if filename.endswith(".png"):
                image_path = os.path.join(folder, filename)
                self.images.append(QPixmap(image_path))
                self.images[-1] = self.images[-1].scaled(int(self.images[-1].width()*scale_factor),
                                                         int(self.images[-1].height()*scale_factor),
                                                         Qt.KeepAspectRatio,
                                                         Qt.SmoothTransformation)
    def get_image(self, index):
        if index < len(self.images):
            return self.images[index]
        else:
            return self.images[0]
    def get_next_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        return self.images[self.index]
    def is_last_image(self):
        return self.index == len(self.images) - 1
    def reset_index(self):
        self.index = 0

