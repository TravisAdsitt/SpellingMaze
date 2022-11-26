from abc import ABC, abstractmethod
import random
from typing import List
import numpy as np
from PIL import Image

from utils.utils import GridDirection

class InvalidColorValue(Exception):
    pass

class Color(tuple):
    def __new__(self, r: int, g: int, b: int):
        return tuple.__new__(Color, [Color.valid_color_value(r), Color.valid_color_value(g), Color.valid_color_value(b)])
    @classmethod
    def valid_color_value(cls, value):
        if value > 255:
            value = 255
        if value < 0:
            value = 0
            
        return value

    @classmethod
    def get_random_color(cls) -> "Color":
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return cls(r, g, b)

class ColorPallete:
    def __init__(self, default_color: Color):
        self.add("default", default_color)
    
    def add(self, key: str, color: Color):
        setattr(self, key, color)


class Drawable2D(ABC):
    def __init__(self, width: int, height: int, default_color: Color = Color(255, 255, 255)):
        self.color_array = [[Color(*default_color) for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        self.pallete = ColorPallete(default_color)

    def fill(self, color: Color):
        width, height, _ = np.shape(self.color_array)
        self.color_array = [[Color(*color) for _ in range(width)] for _ in range(height)]
    
    def valid_pixel(self, x: int, y: int):
        ret_val = True

        if not y < len(self.color_array) or not y >= 0:
            ret_val = False
        
        if not x < len(self.color_array[0]) or not x >= 0:
            ret_val = False

        return ret_val

    def draw_edge(self, direction: GridDirection, color: Color):
        delta_x = 0
        delta_y = 0
        start_x = 0
        start_y = 0

        # Draw Top Edge
        if direction == GridDirection.North:
            delta_x = 1
        if direction == GridDirection.South:
            delta_x = 1
            start_y = self.height - 1
        if direction == GridDirection.East:
            delta_y = 1
            start_x = self.width - 1
        if direction == GridDirection.West:
            delta_y = 1
        
        current_x = start_x
        current_y = start_y

        while self.valid_pixel(current_x, current_y):
            self.color_array[current_y][current_x] = color

            current_y += delta_y
            current_x += delta_x

    def save_array_as_png(self, filename: str):
        color_array = np.array(self.color_array)
        im = Image.fromarray(color_array.astype(np.uint8))
        im.save(filename) 


    def draw_portion(self, start_x: int, start_y: int, input_array: List[List[Color]]):
        for y in range(len(input_array)):
            for x in range(len(input_array[y])):
                self.color_array[start_y + y][start_x + x] = input_array[y][x]


    @abstractmethod
    def draw(self) -> List[List[Color]]:
        raise NotImplementedError()


COLOR_BLACK = Color(0, 0, 0)
COLOR_GRAY = Color(127, 127, 127)
COLOR_WHITE = Color(255, 255, 255)
COLOR_RED   = Color(255, 0, 0)
COLOR_BLUE  = Color(0, 0, 255)
COLOR_GREEN = Color(0, 255, 0)