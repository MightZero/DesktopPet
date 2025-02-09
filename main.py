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
from dialog import Dialog
import random


config=Config()


class Pet:

    def __init__(self):
        self.scale_factor = config.get_setting("scale_factor")

        self.idle_frames = ImageSet("images/idle", self.scale_factor)
        self.run_frames = ImageSet("images/run", self.scale_factor)
        self.jump_up_frames = ImageSet("images/jump_up", self.scale_factor)
        self.jump_down_frames = ImageSet("images/jump_down", self.scale_factor)
        self.dragging_frames = ImageSet("images/dragging", self.scale_factor)

        self.position = Position()
        self.state = State.IDLE.value
        self.key_state = 0
        self.is_grounded = True
        self.is_dragging = False
        self.is_pressing = False

    def update_state(self):
        if self.is_dragging:
            self.state = State.DRAGGING.value
            return

        if self.key_state & KeyState.UP.value and self.is_grounded:
            self.position.jump()
            self.is_grounded = False

        if not self.is_grounded:
            self.state = State.JUMP_DOWN.value if self.position.velocity.y > 0 else State.JUMP_UP.value
        else:
            if self.get_way()!=0:
                self.state = State.RUN.value
            else:
                self.state = State.IDLE.value
                
        if self.position.velocity.x > eps:
            self.position.facing = 1 if self.position.velocity.x > 0 else -1

    def get_current_pixmap(self):
        if self.state & State.DRAGGING.value:
            frames = self.dragging_frames
        elif self.state & State.JUMP_UP.value:
            frames = self.jump_up_frames
        elif self.state & State.JUMP_DOWN.value:
            frames = self.jump_down_frames
        elif self.state & State.RUN.value:
            frames = self.run_frames
        else:
            frames = self.idle_frames

        pixmap = frames.get_next_image()
        return pixmap.transformed(QTransform().scale(self.position.facing, 1))

    def get_position(self):
        self.position.set_acceleration(self.get_way())
        self.position.apply_physics()
        self.is_grounded = self.position.is_grounded()
        
        return [self.position.position.x, self.position.position.y]

    def get_way(self):
        return int(self.key_state & KeyState.RIGHT.value > 0)-int(self.key_state & KeyState.LEFT.value > 0)

class Main(QLabel):
    positionChanged = Signal()  
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.animation_speed = config.get_setting("animation_tps")
        self.physics_speed = config.get_setting("position_tps")
        self.pet = Pet()

        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.start(1000.0 / self.physics_speed)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(1000.0 / self.animation_speed)
        
        self.hasDialog = False

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.dragging = False
        self.drag_position = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)

    def update_position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.pet.position.update_screen_params(
            (self.width(), self.height()),
            (screen.width(), screen.height())
        )
        new_x, new_y = self.pet.get_position()
        self.move(new_x, new_y)
        self.positionChanged.emit()
    def update_animation(self):
        self.pet.update_state()
        pixmap = self.pet.get_current_pixmap()
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pet.is_pressing = True
            self.drag_position = event.globalPos() - self.pos()
        elif event.button() == Qt.RightButton:
            self.close()
            exit(0)

    def mouseMoveEvent(self, event):
        if self.pet.is_pressing:
            self.pet.is_dragging = True
            self.position_timer.stop()
        if self.pet.is_dragging:
            screen = QApplication.primaryScreen().availableGeometry()
            new_pos = event.globalPos() - self.drag_position
            new_x = max(-0.2 * self.width(), min(new_pos.x(), screen.width() - 0.8 * self.width()))
            new_y = max(-0.2 * self.height(), min(new_pos.y(), screen.height() - 0.8 * self.height()))
            self.pet.position.force_move(new_x, new_y)
            self.move(new_x, new_y)
            self.positionChanged.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pet.is_pressing = False
            if not self.hasDialog and not self.pet.is_dragging:
                Dialog(random.choice(config.get_setting("messages")), self)
            self.pet.is_dragging = False
            self.position_timer.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.pet.key_state |= KeyState.LEFT.value
        elif event.key() == Qt.Key_Right:
            self.pet.key_state |= KeyState.RIGHT.value
        elif event.key() == Qt.Key_Up:
            self.pet.key_state |= KeyState.UP.value

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.pet.key_state &= ~KeyState.LEFT.value
        elif event.key() == Qt.Key_Right:
            self.pet.key_state &= ~KeyState.RIGHT.value
        elif event.key() == Qt.Key_Up:
            self.pet.key_state &= ~KeyState.UP.value

if __name__ == "__main__":
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland' or os.environ.get('WAYLAND_DISPLAY'):
        sys.stderr.write("Warning: Detected Wayland")
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
    app = QApplication(sys.argv)
    pet_window = Main()
    pet_window.show()
    sys.exit(app.exec())