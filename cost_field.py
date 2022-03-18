import numpy as np


class CostField:
    def __init__(self, field_size, cell_size):
        self.field_size = field_size
        self.cell_size = cell_size
        self.fields = {}
        self.origin = (0, 0)

    # make sure field_pos is integer values (or maybe rounded floats idk)
    def __add_field(self, field_pos, field):
        self.fields[field_pos] = field

