from math import cos, sin

import numpy as np

class Robot:
    def __init__(self, pos: np.array, angle: float):
        self.pos = pos
        self.angle = angle
        self.throttle = 0.0
        self.steer = 0.0

    def update(self, dt):
        self.angle += self.steer * dt
        self.pos += np.array([cos(self.angle), sin(self.angle)]) * self.throttle * dt

    def render(self):
        pass