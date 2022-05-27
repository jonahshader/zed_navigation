from math import floor

import numpy as np

class SingleCostField:
    def __init__(self, field_size=16, cell_size=.25, translate_threshold=2):
        self.field_size = field_size
        self.cell_size = cell_size
        self.translate_threshold = translate_threshold
        self.offset = np.array([0, 0])
        self.field = np.zeros(floor(field_size/cell_size), floor(field_size/cell_size))

    def get_cost(self, point: np.ndarray) -> float:
        point_in_field = (point + self.offset) / self.cell_size
        if not self._in_field(point_in_field):
            return

    def add_point(self, point: np.ndarray):
        point_in_field = ((point + self.offset) / self.cell_size).astype(dtype=np.int)
        if not self._in_field(point_in_field):
            return

    def render(self):
        y = 
        for row in self.field:


    def _in_field(self, transformed_point: np.ndarray):
        return 0 <= transformed_point[0] < self.field.size and 0 <= transformed_point[1] < self.field
