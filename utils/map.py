from enum import Enum
from utils.drawable import COLOR_BLACK, COLOR_GRAY, COLOR_GREEN, COLOR_RED, COLOR_WHITE, Drawable2D, Color
from typing import List, Tuple
import numpy as np
import random

from utils.utils import GridDirection

class ObservableList(list):
    def __init__(self, list_in: List = None):
        if not list_in:
            list_in = []
        self._has_changed = False
        super().__init__(list_in)
    
    def remove(self, __value) -> None:
        self._has_changed = True
        return super().remove(__value)

    def append(self, __object) -> None:
        self._has_changed = True
        return super().append(__object)
    
    


class Block(Drawable2D):
    def __init__(self, width: int, height: int, entry_direction: GridDirection = None, exit_directions: List[GridDirection] = None):
        super().__init__(width, height)

        self.pallete.add("wall_color", COLOR_BLACK)
        self.pallete.add("background_color", COLOR_GRAY)

        self.exit_directions = exit_directions if exit_directions else []
        self.explored = False
        self._has_changed = True

    @property
    def entry_direction(self):
        if not hasattr(self, "_entry_direction"):
            self._entry_direction = None

        return self._entry_direction
    
    @entry_direction.setter
    def entry_direction(self, direction: GridDirection):
        self._has_changed = True
        self._entry_direction = direction
    
    @property
    def exit_directions(self):
        if not hasattr(self, "_exit_directions"):
            self._exit_directions = ObservableList()
        
        return self._exit_directions
    
    @exit_directions.setter
    def exit_directions(self, directions: List[GridDirection]):
        if not directions:
            return 

        self._exit_directions = ObservableList(directions)

    def draw(self) -> List[List[Color]]:
        """Draw our block in 2D"""
        if not self._has_changed and not self.exit_directions._has_changed:
            return None

        if not self.explored:
            self.fill(COLOR_BLACK)
        else:
            self.fill(self.pallete.background_color)

        for direction in GridDirection:
            if direction not in self.exit_directions and direction != self.entry_direction:
                self.draw_edge(direction, self.pallete.wall_color)

        self._has_changed = False
        return self.color_array

class Map(Drawable2D):
    def __init__(self, grid_width: int, grid_height: int, block_width: int = 10, block_height: int = 10):
        super().__init__(grid_width * block_width, grid_height * block_height)

        self.grid_width = grid_width
        self.grid_height = grid_height

        self.block_width = block_width
        self.block_height = block_height

        self.block_grid = [[Block(self.block_width, self.block_height) for _ in range(self.grid_width)] for _ in range(self.grid_height)]

    def get_start_block(self):
        return random.choice(self.block_grid[0])

    def get_block_x_y_tuple(self, block: Block, clear_cache: bool = False) -> Tuple[int, int]:
        if not hasattr(self, "_cached_block_locations") or clear_cache:
            self._cached_block_locations = {}
        
        if block in self._cached_block_locations:
            return self._cached_block_locations[block]

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.block_grid[y][x] == block:
                    self._cached_block_locations[block] = (x, y)
                    return (x, y)
        
        return (-1, -1)
    
    def get_block_in_direction(self, block: Block, direction: GridDirection, ignore_explored: bool = True) -> None or Block:
        x, y = self.get_block_x_y_tuple(block)

        if x == -1 or y == -1:
            return None
        
        check_x = x
        check_y = y
        if direction == GridDirection.North:
            check_y -= 1
        if direction == GridDirection.South:
            check_y += 1
        if direction == GridDirection.West:
            check_x -= 1
        if direction == GridDirection.East:
            check_x += 1
        
        if check_y >= self.grid_height or check_y < 0:
            return None
        
        if check_x >= self.grid_width or check_x < 0:
            return None
        
        if ignore_explored and self.block_grid[check_y][check_x].explored:
            return None
        
        return self.block_grid[check_y][check_x]

    
    def draw(self) -> List[List[Color]]:
        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                block_color_data = self.block_grid[y][x].draw()
                if block_color_data:
                    self.draw_portion(x * self.block_width, y * self.block_height, block_color_data)
        
        return self.color_array

class Path:
    def __init__(self, map: Map, start_block: Block, min_path_length: int = 1):
        self.map = map
        self.blocks = [start_block]
        self.min_path_length = min_path_length
        # self.path_color = Color.get_random_color()

        self.complete = False
    
    def get_blocks_in_all_directions(self, block: Block, ignore_explored: bool = True) -> List[Tuple[GridDirection, Block]]:
        ret_val = []

        for direction in GridDirection:
            curr_block = self.map.get_block_in_direction(block, direction, ignore_explored)
            if curr_block:
                ret_val.append((direction, curr_block))
        
        return ret_val

    def clean_block_relationships(self, block: Block):
        for direction, check_block in self.get_blocks_in_all_directions(block, False):
            check_relative_direction = GridDirection.get_opposite_direction(direction)

            # Check Block has no relationship to this block
            if direction != block.entry_direction and direction not in block.exit_directions:
                # Make sure the other block isn't exiting or entering from our direction
                if check_relative_direction == check_block.entry_direction:
                    check_block.entry_direction = None
                if check_relative_direction in check_block.exit_directions:
                    check_block.exit_directions.remove(check_relative_direction)

    def clean_path_walls(self):
        for block in self.blocks:
            entry = block.entry_direction
            exits = block.exit_directions

            self.clean_block_relationships(block)

            block.entry_direction = entry
            block.exit_directions = exits


    def set_random_exits(self, block: Block, chance: float = 0.6) -> List[Block]:
        ret_val = list()

        for direction, check_block in self.get_blocks_in_all_directions(block):
            if check_block and random.randint(1, 100) < int(chance * 100):
                block.exit_directions.append(direction)
                check_block.entry_direction = GridDirection.get_opposite_direction(direction)
                ret_val.append(check_block)
        
        return ret_val

    def step_path(self) -> List[Block]:
        ret_blocks = []

        if self.complete:
            return ret_blocks
        
        current_block = self.blocks[-1]
        current_block.explored = True
        # current_block.pallete.background_color = self.path_color

        exit_block_list = self.set_random_exits(current_block)

        while exit_block_list:
            current_block = random.choice(exit_block_list)
            exit_block_list.remove(current_block)

            if current_block in ret_blocks:
                ret_blocks.remove(current_block)

            current_block.explored = True
            ret_blocks.extend(exit_block_list)

            exit_block_list = self.set_random_exits(current_block)
            # self.clean_block_relationships(current_block)
            self.blocks.append(current_block)

        self.complete = True

        return ret_blocks


class Maze:
    def __init__(self, width: int, height: int) -> Tuple[int, Block]:
        self.map = Map(width, height)
        self.paths = list()

    def get_lowest_block(self):
        for y in range(self.map.grid_height - 1, -1, -1):
            explored_blocks = [block.explored for block in self.map.block_grid[y]]
            if any(explored_blocks):
                
                explored_low_blocks = [block for block in self.map.block_grid[y] if block.explored]

                return (y, random.choice(explored_low_blocks))
        
        return None

    def generate_maze(self):
        self.map_start = self.map.get_start_block()
        self.map_end = None

        self.map_start.entry_direction = GridDirection.North

        possible_path_starts = [self.map_start] 
        while not self.map_end:
            while possible_path_starts:
                current_start = random.choice(possible_path_starts)
                possible_path_starts.remove(current_start)

                if current_start.explored:
                    continue

                path = Path(self.map, current_start)
                while not path.complete:
                    possible_path_starts.extend(path.step_path())
                
                path.clean_path_walls()
            
            y, lowest_block = self.get_lowest_block()
            lowest_block.exit_directions.append(GridDirection.South)

            if y == self.map.grid_height - 1:
                self.map_end = lowest_block
            else:
                new_start = self.map.get_block_in_direction(lowest_block, GridDirection.South)
                new_start.entry_direction = GridDirection.North
                possible_path_starts.append(new_start)


        self.map_start.pallete.background_color = COLOR_GREEN
        self.map_end.pallete.background_color = COLOR_RED
        self.map.draw()
        

    
    def save_image(self, filename: str):
        return self.map.save_array_as_png(filename)
         
      



