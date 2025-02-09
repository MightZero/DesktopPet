from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent
import sys
import os

class Position:

    def __init__(self, scale_factor):
        self.x = 0
        self.y = 0
        self.facing = 1
        self.scale_factor = scale_factor

        self.velocity_y = 0
        self.gravity = 1.5 * scale_factor
        self.jump_force = -90 * scale_factor * scale_factor
        self.ground_y = 0

        self.velocity_x = 0
        self.acceleration = 5 * scale_factor
        self.max_speed = 15 * scale_factor
        self.friction = 0.85

        self.window_width = 0
        self.screen_width = 0

    def update_screen_params(self, window_size, screen_size):
        self.window_width, window_height = window_size
        self.screen_width, self.screen_height = screen_size
        self.ground_y = screen_size[1] - window_height

    def apply_physics(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        self.velocity_x *= self.friction
        self.x += self.velocity_x

        self.x = max(-0.2 * self.window_width, self.x)
        self.x = min(self.x, self.screen_width - 0.8 * self.window_width)
        
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity_y = 0
            return True
        return False

    def jump(self):
        if self.y >= self.ground_y:
            self.velocity_y = self.jump_force
