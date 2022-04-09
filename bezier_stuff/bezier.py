import numpy as np


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

    def lookup_t(self, distance):
        valid_index = -1
        for idx, val in enumerate(self._lut):
            if val[0] > distance:
                valid_index = idx - 1
                break
        if valid_index == -1:
            if self._lut[-1][0] <= distance:
                return 1
        if valid_index < 0:
            return 0
        elif valid_index >= len(self._lut):
            return 1
        else:
            dist0, t0 = self._lut[valid_index]
            dist1, t1 = self._lut[valid_index + 1]
            p = (distance - dist0) / (dist1 - dist0)
            t = (1 - p) * t0 + p * t1
            return t
