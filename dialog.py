
from enum import IntFlag
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, Signal
import sys
import os
from util import State, KeyState, eps
from images import ImageSet
from position import Position
from config import Config

class Dialog(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.parent.positionChanged.connect(self.update_position)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # 设置样式
        self.setStyleSheet("""
            FadingDialog {
                background: rgba(40, 40, 40, 220);
                border-radius: 8px;
                padding: 12px 20px;
                color: #f0f0f0;
                font-family: Microsoft YaHei;
                font-size: 14px;
                min-width: 120px;
                qproperty-alignment: AlignCenter;
            }
            FadingDialog::shadow {
                padding: 10px;
                background: rgba(0, 0, 0, 50);
                border-radius: 12px;
            }
        """)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        self.setText(text)
        self.adjustSize()

        # 设置显示位置
        if parent:
            pos = parent.pos()
            self.move(
                pos.x() + parent.width() // 2 - self.width() // 2,
                pos.y() - self.height() - 10
            )
            parent.hasDialog=True
        # 自动关闭定时器
        QTimer.singleShot(1000, self.fade_out)
        self.show()

    def update_position(self):
        if self.parent and self.parent.isVisible():
            pos = self.parent.pos()
            new_x = pos.x() + self.parent.width() // 2 - self.width() // 2
            new_y = pos.y() - self.height() - 10

            # 边界检查
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))

            self.move(new_x, new_y)
    def fade_out(self):
        # 淡出动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()
        self.parent.hasDialog=False