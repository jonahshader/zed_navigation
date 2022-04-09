import arcade
from pyglet.math import Vec2
import numpy as np

from bezier_stuff import bezier

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Bezier Curve Demo"


class BezierCurveDemo(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.WHITE)
        self.time = 0

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.move(Vec2(-self.width / 2, -self.height / 2))

        self.p0 = np.array([0, 0])
        self.p1 = np.array([35, 35])
        self.p2 = np.array([70, 0])
        self.p3 = np.array([-50, -10])

        self.lut = bezier.LUT()

        self.b = lambda t: bezier.b_cubic(self.p0, self.p1, self.p2, self.p3, t)

    def setup(self):
        self.time = 0  # ??

    def on_draw(self):
        self.camera.use()
        arcade.start_render()
        arcade.draw_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1], arcade.csscolor.GRAY)
        # arcade.draw_line(self.p1[0], self.p1[1], self.p2[0], self.p2[1], arcade.csscolor.GRAY)
        arcade.draw_line(self.p2[0], self.p2[1], self.p3[0], self.p3[1], arcade.csscolor.GRAY)
        # for i in range(0, 26):
        #     point = self.b(i/25)
        #     arcade.draw_point(point[0], point[1], arcade.csscolor.BLACK, 4)

        self.lut.generate(self.b, samples=50)
        dist = self.lut.distance
        for i in range(0, 26):
            curr_dist = (i / 25) * dist
            t = self.lut.lookup_t(curr_dist)
            point = self.b(t)
            arcade.draw_point(point[0], point[1], arcade.csscolor.GREEN, 4)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        self.on_mouse_down(x, y, buttons, modifiers)

    def on_mouse_down(self, x: float, y: float, button: int, modifiers: int):
        # find closest point to mouse
        xw = x + self.camera.position[0]
        yw = y + self.camera.position[1]
        mousepos = np.array([xw, yw])

        l0 = np.linalg.norm(self.p0 - mousepos)
        l1 = np.linalg.norm(self.p1 - mousepos)
        l2 = np.linalg.norm(self.p2 - mousepos)
        l3 = np.linalg.norm(self.p3 - mousepos)

        mindist = min(l0, l1, l2, l3)
        if mindist == l0:
            self.p0 = np.copy(mousepos)
        elif mindist == l1:
            self.p1 = np.copy(mousepos)
        elif mindist == l2:
            self.p2 = np.copy(mousepos)
        elif mindist == l3:
            self.p3 = np.copy(mousepos)

    def on_update(self, delta_time: float):
        self.time += delta_time


def main():
    window = BezierCurveDemo()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
