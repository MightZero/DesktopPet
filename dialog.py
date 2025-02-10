from PySide6.QtWidgets import QApplication, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation

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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        self.setText(text)
        self.adjustSize()

        
        if parent:
            pos = parent.pos()
            self.move(
                pos.x() + parent.width() // 2 - self.width() // 2,
                pos.y() - self.height() - 10
            )
            parent.hasDialog=True
        
        QTimer.singleShot(1000, self.fade_out)
        self.show()

    def update_position(self):
        if self.parent and self.parent.isVisible():
            pos = self.parent.pos()
            new_x = pos.x() + self.parent.width() // 2 - self.width() // 2
            new_y = pos.y() - self.height() - 10

            
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))

            self.move(new_x, new_y)
    def fade_out(self):
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()
        self.parent.hasDialog=False