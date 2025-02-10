import math
from config import Config
config = Config()
import math
from util import Vector2D
class Position:
    def __init__(self):
        self.scale_factor = config.get_setting("scale_factor")
        self.tps = config.get_setting("position_tps")
        self.max_acceleration = config.get_setting("physics")["acceleration"] * self.scale_factor
        self.friction = config.get_setting("physics")["friction"]
        self.air_resistance = config.get_setting("physics")["air_resistance"]
        self.gravity = Vector2D(0, config.get_setting("physics")["gravity"])
        self.jump_force = Vector2D(0, -config.get_setting("physics")["jump_force"] * math.sqrt(self.scale_factor))

        self.tps_factor = 60.0 / self.tps
        self.facing = 1
        self.ground_y = 0
        self.screen_height = 0
        self.screen_width = 0
        self.window_width = 0

        self.position = Vector2D(0, 0)
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
    def update_screen_params(self, window_size, screen_size):
        self.window_width, window_height = window_size
        self.screen_width, self.screen_height = screen_size
        self.ground_y = screen_size[1] - window_height + config.get_setting("ground_offset")
    def apply_physics(self):
        self.velocity += self.gravity
        self.velocity.y += self.acceleration.y
        if self.is_grounded():
            self.velocity -= self.velocity * self.friction
            self.velocity.x += self.acceleration.x
        else:
            self.velocity -= self.velocity * self.air_resistance
            self.velocity.x += self.acceleration.x * self.air_resistance
        self.position += self.velocity * self.tps_factor
        self.position.x = max(-0.2 * self.window_width, self.position.x)
        self.position.x = min(self.position.x, self.screen_width - 0.8 * self.window_width)
        if self.position.y >= self.ground_y:
            self.position.y = self.ground_y
            self.velocity.y = 0
        if self.velocity.x != 0:
            self.facing = 1 if self.velocity.x > 0 else -1
    def force_move(self, new_x, new_y):
        self.position = Vector2D(new_x, new_y)
    def jump(self):
        if self.is_grounded():
            self.velocity += self.jump_force
    def is_grounded(self):
        return self.position.y >= self.ground_y
    def is_running(self):
        return abs(self.velocity.x) > 2 * self.scale_factor
    def set_acceleration(self, way):
        if way < 0:
            self.acceleration.x = -self.max_acceleration
        elif way > 0:
            self.acceleration.x = self.max_acceleration
        else:
            self.acceleration.x = 0
    def set_velocity(self, velocity):
        self.velocity = velocity
    def velocity_magnitude(self):
        return self.velocity.magnitude()