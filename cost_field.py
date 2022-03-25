import math

import arcade

import numpy as np


class CostField:
    # cell_size is in meters
    # field_size is in cell_size
    def __init__(self, field_size=32, cell_size=.25, field_load_radius=4, field_unload_radius=7, beta=0.9):
        self.field_size = field_size
        self.cell_size = cell_size
        self.field_load_radius = field_load_radius
        self.field_unload_radius = field_unload_radius
        self.beta = beta
        self.fields = {}
        self.origin = (0, 0)

    def add_point(self, point):
        # continue if point will be placed into loaded field
        # if it is

        field = self.__get_field_at_point(point)
        if field is not None:
            point_in_field = (math.floor(point[0] / self.cell_size) % self.field_size,
                              math.floor(point[1] / self.cell_size) % self.field_size)
            field[point_in_field[0], point_in_field[1]] += (1 - self.beta)

    def update(self, cam_pos):
        # iterate through a square of field pos around cam_pos
        # unload things outside unload radius
        # load (construct) things inside load radius
        pass

    def display_all_fields(self, pixels_per_meter):
        for field_pos, field in self.fields:
            self.__display_field(field_pos, field, pixels_per_meter)

    def __display_field(self, field_pos, field, pixels_per_meter):
        field_screen_pos = (field_pos[0] * self.field_size * self.cell_size, field_pos[1] * self.field_size * self.cell_size)
        y = field_pos[1]

        cell_render_size = self.cell_size * pixels_per_meter

        for row in field:
            x = field_pos[0]
            for val in row:
                # use x, y
                cell_screen_pos = (x * cell_render_size, y * cell_render_size)
                brightness = round(min(val, 255))
                color = (brightness, brightness, brightness)
                arcade.draw_rectangle_filled(cell_screen_pos[0], cell_screen_pos[1], cell_render_size, cell_render_size, color)
                x += 1
            y += 1


    def __get_field_at_point(self, point):
        field_pos = (math.floor((point[0] / self.cell_size) / self.field_size),
                     math.floor((point[1] / self.cell_size) / self.field_size))
        if field_pos in self.fields:
            return self.fields[field_pos]
        else:
            return None
        pass

    # make sure field_pos is integer values (or maybe rounded floats idk)
    def __add_field(self, field_pos, field):
        self.fields[field_pos] = field
