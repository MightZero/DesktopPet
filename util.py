from enum import IntFlag


class State(IntFlag):
    IDLE = 1
    RUN = 2
    JUMP_UP = 4
    JUMP_DOWN = 8
    DRAGGING = 16
class KeyState(IntFlag):
    LEFT = 1
    RIGHT = 2
    UP = 4
    
eps = 1e-5
def precision(x):
    if abs(x)<eps: 
        return 0.0
    else: 
        return x

class Vector2D:
    def __init__(self, x=0.0, y=0.0):
        self.x = precision(x)
        self.y = precision(y)

    def __add__(self, other):
        return Vector2D(precision(self.x + other.x), precision(self.y + other.y))

    def __sub__(self, other):
        return Vector2D(precision(self.x - other.x), precision(self.y - other.y))

    def __mul__(self, scalar):
        return Vector2D(precision(self.x * scalar), precision(self.y * scalar))

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector2D(precision(self.x / scalar), precision(self.y / scalar))

    def magnitude(self):
        return precision(math.sqrt(self.x * self.x + self.y * self.y))

    def normalize(self):
        mag = self.magnitude()
        if mag < eps:
            return Vector2D(0, 0)
        return Vector2D(precision(self.x / mag), precision(self.y / mag))

    def dot(self, other):
        return precision(self.x * other.x + self.y * other.y)

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

    def __setitem__(self, index, value):
        if index == 0:
            self.x = precision(value)
        elif index == 1:
            self.y = precision(value)
        else:
            raise IndexError("Index out of range")

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")