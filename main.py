from enum import IntFlag
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QPoint, QTimer
import sys
import os
from util import State, KeyState
from images import ImageSet
from position import  Position

class State(IntFlag):
    IDLE = 1
    RUN = 2
    JUMP_UP = 4
    JUMP_DOWN = 8
    DRAGGING = 16

class Pet:

    def __init__(self, scale_factor, animation_speed):
        self.scale_factor = scale_factor
        self.animation_speed = animation_speed

        self.idle_frames = ImageSet("images/idle", scale_factor)
        self.run_frames = ImageSet("images/run", scale_factor)
        self.jump_up_frames = ImageSet("images/jump_up", scale_factor)
        self.jump_down_frames = ImageSet("images/jump_down", scale_factor)
        self.dragging_frames = ImageSet("images/dragging", scale_factor)

        self.state = State.IDLE.value
        self.key_state = 0
        self.is_grounded = True

    def update_state(self, position, is_dragging=False):
        if is_dragging:
            self.state = State.DRAGGING.value
            return

        if self.key_state & KeyState.UP.value and self.is_grounded:
            position.jump()
            self.is_grounded = False

        if not self.is_grounded:
            self.state = State.JUMP_DOWN.value if position.velocity_y > 0 else State.JUMP_UP.value
        else:
            if abs(position.velocity_x) > 2:
                self.state = State.RUN.value
            else:
                self.state = State.IDLE.value

        if position.velocity_x != 0:
            position.facing = 1 if position.velocity_x > 0 else -1

    def get_current_pixmap(self, facing):
        
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
        return pixmap.transformed(QTransform().scale(facing, 1))

class Main(QLabel):

    def __init__(self, scale_factor=1.0, animation_speed=100):
        super().__init__()
        self.scale_factor = scale_factor
        self.initUI()

        self.position = Position(scale_factor)
        self.pet = Pet(scale_factor, animation_speed)

        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.update_physics)
        self.physics_timer.start(16)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(animation_speed)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.dragging = False
        self.drag_position = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)

    def update_physics(self):
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.position.update_screen_params(
            (self.width(), self.height()),
            (screen.width(), screen.height())
        )

        left = self.pet.key_state & KeyState.LEFT.value
        right = self.pet.key_state & KeyState.RIGHT.value

        if left and not right:
            self.position.velocity_x = max(
                -self.position.max_speed,
                self.position.velocity_x - self.position.acceleration
            )
        elif right and not left:
            self.position.velocity_x = min(
                self.position.max_speed,
                self.position.velocity_x + self.position.acceleration
            )

        self.pet.is_grounded = self.position.apply_physics()
        self.move(self.position.x, self.position.y)

    def update_animation(self):
        self.pet.update_state(self.position, self.dragging)
        pixmap = self.pet.get_current_pixmap(self.position.facing)
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.physics_timer.stop()
            self.drag_position = event.globalPos() - self.pos()
        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        if self.dragging:
            screen = QApplication.primaryScreen().availableGeometry()
            new_pos = event.globalPos() - self.drag_position
            new_x = max(-0.2 * self.width(), min(new_pos.x(), screen.width() - 0.8 * self.width()))
            new_y = max(-0.2 * self.height(), min(new_pos.y(), screen.height() - 0.8 * self.height()))
            self.position.x, self.position.y = new_x, new_y
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.physics_timer.start()

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
    pet_window = Main(scale_factor=0.2)
    pet_window.show()
    sys.exit(app.exec())