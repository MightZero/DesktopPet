from enum import IntFlag


class State(IntFlag):
    IDLE = 1
    RUN = 2
    JUMP = 4
class KeyState(IntFlag):
    LEFT = 1
    RIGHT = 2
    UP = 4