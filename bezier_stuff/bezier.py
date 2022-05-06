import arcade
import numpy as np
from typing import List, Tuple


class Bezier:
    def __init__(self, p0: np.ndarray, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, samples=50):
        self.pts: List[np.ndarray] = [p0, p1, p2, p3]
        self.samples = samples
        self.stale = True
        self.lut = LUT()
        self.b = lambda t: b_cubic(self.pts[0], self.pts[1], self.pts[2], self.pts[3], t)

    def copy(self):
        return Bezier(np.copy(self.pts[0]), np.copy(self.pts[1]), np.copy(self.pts[2]), np.copy(self.pts[3]))

    def copyfrom(self, bezier):
        for i in range(len(self.pts)):
            self.set_point(bezier.pts[i], i)

    def get_distance(self) -> float:
        if self.stale:
            self.lut.generate(self.b, self.samples)
            self.stale = False
        return self.lut.distance

    def render(self, scale, offset):
        dist = self.get_distance()
        for i in range(self.samples):
            curr_dist = (i / (self.samples - 1)) * dist
            point = self.get(curr_dist)
            arcade.draw_point(point[0] * scale + offset[0], point[1] * scale + offset[1], arcade.csscolor.GREEN, 4)


    def mutate(self, amount):
        for p in self.pts:
            p += np.random.normal(scale=amount, size=p.size)
        self.stale = True

    def mutate_point(self, amount, index):
        self.pts[index] += np.random.normal(scale=amount, size=self.pts[index].size)
        self.stale = True

    def set_point(self, point: np.ndarray, index: int):
        np.copyto(self.pts[index], point)
        self.stale = True

    def get(self, distance) -> Tuple:
        if self.stale:
            self.lut.generate(self.b, self.samples)
            self.stale = False
        return self.b(self.lut.lookup_t(distance))
        # return self.lut.lookup_t(distance)

def make_straight_bezier(start_point: np.ndarray, end_point: np.ndarray, samples=50) -> Bezier:
    return Bezier(start_point, start_point * (2/3) + end_point * (1/3), start_point * (1/3) + end_point * (2/3), end_point, samples=samples)


def lerp(p0, p1, t):
    return (1 - t) * p0 + t * p1


def b_cubic(p0, p1, p2, p3, t):
    p01 = lerp(p0, p1, t)
    p12 = lerp(p1, p2, t)
    p23 = lerp(p2, p3, t)

    p0112 = lerp(p01, p12, t)
    p1223 = lerp(p12, p23, t)
    p011223 = lerp(p0112, p1223, t)
    return p011223


def b_dist(b, samples=100):
    dist = 0
    pp = b(0)
    for i in range(1, samples + 1):
        t = i / samples
        p = b(t)
        dist += np.linalg.norm(b(t) - pp)
        pp = p

    return dist


# class Bezier:
#     def __init__(self):
#

class LUT:
    def __init__(self):
        self._lut = []
        self.distance = 0

    def generate(self, b, samples=100):
        dist = 0
        pp = b(0)
        self._lut.clear()
        self._lut.append((dist, 0))
        for i in range(1, samples + 1):
            t = i / samples
            p = b(t)
            dist += np.linalg.norm(b(t) - pp)
            self._lut.append((dist, t))
            pp = p
        self.distance = dist

    def lookup_t(self, distance) -> float:
        valid_index = -1
        for idx, val in enumerate(self._lut):
            if val[0] > distance:
                valid_index = idx - 1
                break
        if valid_index == -1:
            if self._lut[-1][0] <= distance:
                return 1.0
        if valid_index < 0:
            return 0.0
        elif valid_index >= len(self._lut):
            return 1.0
        else:
            dist0, t0 = self._lut[valid_index]
            dist1, t1 = self._lut[valid_index + 1]
            p = (distance - dist0) / (dist1 - dist0)
            t = (1 - p) * t0 + p * t1
            return t
