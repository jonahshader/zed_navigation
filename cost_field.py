import math
from typing import Tuple

import arcade

import numpy as np


def _field_to_field_dist(f1_pos, f2_pos):
    return math.sqrt(pow(f1_pos[0] - f2_pos[0], 2) + pow(f1_pos[1] - f2_pos[1], 2))


def _world_pos_to_screen(world_pos, pixels_per_meter, offset):
    return world_pos[0] * pixels_per_meter + offset[0], world_pos[1] * pixels_per_meter + offset[1]


class CostField:
    # cell_size is in meters
    # field_size is in cell_size
    def __init__(self, field_size=8, cell_size=.25, field_load_radius=2, field_unload_radius=20, beta=0.99):
        self.field_size = field_size
        self.cell_size = cell_size
        self.field_load_radius = field_load_radius
        self.field_unload_radius = field_unload_radius
        self.beta = beta
        self.fields = {}
        self.cam_pos = (0, 0)

    def add_point(self, point):
        # continue if point will be placed into loaded field
        # if it is

        field = self.__get_field_at_point(point)
        if field is not None:
            point_in_field = (math.floor(point[0] / self.cell_size) % self.field_size,
                              math.floor(point[1] / self.cell_size) % self.field_size)
            newval = field[point_in_field[1], point_in_field[0]] + (1 - self.beta)
            field[point_in_field[1], point_in_field[0]] = min(newval, 1.0)

    def update(self, cam_pos):
        self.cam_pos = cam_pos
        # calculate cam field pos
        cam_field_pos = self.__world_pos_to_field(cam_pos)

        # unload things outside unload radius
        to_remove = []
        for field_pos, field in self.fields.items():
            if _field_to_field_dist(field_pos, cam_field_pos) > self.field_unload_radius:
                to_remove.append(field_pos)
            else:
                field *= self.beta
        for k in to_remove:
            self.fields.pop(k)

        # load things inside load radius
        for y in range(-self.field_load_radius, self.field_load_radius + 1):
            for x in range(-self.field_load_radius, self.field_load_radius + 1):
                pos = (cam_field_pos[0] + x, cam_field_pos[1] + y)
                if pos not in self.fields:
                    self.__make_field(pos)

    # TODO: make bilinear interpolated version

    def get_cost(self, point) -> float:
        """point can be either tuple or np.ndarray"""
        field = self.__get_field_at_point(point)
        if field is not None:
            point_in_field = (math.floor(point[0] / self.cell_size) % self.field_size,
                              math.floor(point[1] / self.cell_size) % self.field_size)
            return field[point_in_field[1], point_in_field[0]]
        else:
            return 1.0

    def display_all_fields(self, pixels_per_meter, offset):
        for field_pos, field in self.fields.items():
            # print(self.fields)
            self.__display_field(field_pos, field, pixels_per_meter, offset)
        cam_screen_pos = _world_pos_to_screen(self.cam_pos, pixels_per_meter, offset)
        arcade.draw_circle_filled(cam_screen_pos[0], cam_screen_pos[1], .1 * pixels_per_meter, arcade.color.BLUE)

    def __display_field(self, field_pos, field, pixels_per_meter, offset):
        # field_screen_pos = (
        #     field_pos[0] * self.field_size * self.cell_size,
        #     field_pos[1] * self.field_size * self.cell_size)
        y = field_pos[1] * self.field_size

        cell_render_size = self.cell_size * pixels_per_meter

        for row in field:
            x = field_pos[0] * self.field_size
            for val in row:
                # use x, y
                cell_screen_pos = (x * cell_render_size, y * cell_render_size)
                brightness = round(min(val, 1) * 255)
                color = (brightness, brightness, brightness)
                if x == 0 and y == 0:
                    color = (255, 0, 0)
                arcade.draw_rectangle_filled(cell_screen_pos[0] + offset[0], cell_screen_pos[1] + offset[1], cell_render_size, cell_render_size,
                                             color)
                # print(f'drawing rectangle at {cell_screen_pos[0]} {cell_screen_pos[1]} of brightness {brightness}')
                x += 1
            y += 1

    def __get_field_at_point(self, point):
        field_pos = self.__world_pos_to_field(point)
        if field_pos in self.fields:
            return self.fields[field_pos]
        else:
            return None

    def __world_pos_to_field(self, point):
        field_pos = (math.floor((point[0] / self.cell_size) / self.field_size),
                     math.floor((point[1] / self.cell_size) / self.field_size))
        return field_pos

    # # make sure field_pos is integer values (or maybe rounded floats idk)
    # def __add_field(self, field_pos, field):
    #     self.fields[field_pos] = field

    def __make_field(self, field_pos):
        # field = np.zeros((self.field_size, self.field_size), dtype=float)
        field = np.random.random((self.field_size, self.field_size))
        self.fields[field_pos] = field
