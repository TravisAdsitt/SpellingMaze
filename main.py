from dataclasses import dataclass, field
from enum import Enum
from PIL import Image
import numpy as np
from typing import Tuple, List
import random

WALL_COLOR = [0,0,0]
PATH_COLOR = [127,127,127]
START_BLOCK_COLOR = [0, 255, 0]
END_BLOCK_COLOR = [255, 0, 0]

class BlockDirections(Enum):
    North = "North"
    South = "South"
    West = "West"
    East = "East"

    @classmethod
    def get_opposite_direction(cls, direction: "BlockDirections") -> "BlockDirections":
        if direction == cls.East:
            return cls.West
        if direction == cls.West:
            return cls.East
        if direction == cls.North:
            return cls.South
        if direction == cls.South:
            return cls.North
    
    @classmethod
    def get_x_y_in_direction(cls, direction: "BlockDirections", block: "Block"):
        if direction == BlockDirections.North:
            return (block.grid_x, block.grid_y - 1)
        if direction == BlockDirections.South:
            return (block.grid_x, block.grid_y + 1)
        if direction == BlockDirections.East:
            return (block.grid_x + 1, block.grid_y)
        if direction == BlockDirections.West:
            return (block.grid_x - 1, block.grid_y)


@dataclass
class Block:
    grid_x: int
    grid_y: int
    entry_direction: BlockDirections
    exit_directions: List[BlockDirections] = field(default_factory=list)
    visited: bool = False

    def __eq__(self, other: "Block") -> bool:
        if not isinstance(other, type(self)):
            return False
        
        if other.grid_x != self.grid_x or other.grid_y != self.grid_y:
            return False
        
        return True

def save_array_as_png(filename: str, pixel_array: List[List[int]]):
    im = Image.fromarray(pixel_array)
    im.save(filename)

def get_block_upper_left_pixel(block: Block, block_w: int, block_h: int) -> Tuple[int, int]:
    upper_left_x = block.grid_x * block_w
    upper_left_y = block.grid_y * block_h

    return (upper_left_x, upper_left_y)

def fill_block(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]], color: List[int] = [0, 0, 0]) -> List[List[int]]:
    upper_left_x, upper_left_y = get_block_upper_left_pixel(block, block_w, block_h)
    return_array = np.copy(pixel_array)

    for x in range(0, block_w):
        for y in range(0, block_h):
            return_array[upper_left_y + y][upper_left_x + x] = color
    
    return return_array


def draw_north_edge(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]]) -> List[List[int]]:
    upper_left_x, upper_left_y = get_block_upper_left_pixel(block, block_w, block_h)
    return_array = np.copy(pixel_array)

    for x in range(0, block_w):
        return_array[upper_left_y][upper_left_x + x] = WALL_COLOR
    
    return return_array

def draw_south_edge(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]]) -> List[List[int]]:
    upper_left_x, upper_left_y = get_block_upper_left_pixel(block, block_w, block_h)
    return_array = np.copy(pixel_array)

    for x in range(0, block_w):
        return_array[upper_left_y + block_h - 1][upper_left_x + x] = WALL_COLOR
    
    return return_array

def draw_east_edge(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]]) -> List[List[int]]:
    upper_left_x, upper_left_y = get_block_upper_left_pixel(block, block_w, block_h)
    return_array = np.copy(pixel_array)

    for y in range(0, block_h):
        return_array[upper_left_y + y][upper_left_x + block_w - 1] = WALL_COLOR
    
    return return_array

def draw_west_edge(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]]) -> List[List[int]]:
    upper_left_x, upper_left_y = get_block_upper_left_pixel(block, block_w, block_h)
    return_array = np.copy(pixel_array)

    for y in range(0, block_h):
        return_array[upper_left_y + y][upper_left_x] = WALL_COLOR
    
    return return_array


def draw_block_walls(block: Block, block_w: int, block_h: int, pixel_array: List[List[int]]) -> List[List[int]]:
    return_array = np.copy(pixel_array)
    
    for direction in BlockDirections:
        if direction != block.entry_direction and direction not in block.exit_directions:
            if direction == BlockDirections.North:
                return_array = draw_north_edge(block, block_w, block_h, return_array)
            if direction == BlockDirections.South:
                return_array = draw_south_edge(block, block_w, block_h, return_array)
            if direction == BlockDirections.East:
                return_array = draw_east_edge(block, block_w, block_h, return_array)
            if direction == BlockDirections.West:
                return_array = draw_west_edge(block, block_w, block_h, return_array)

    

    return return_array



# Determine Start and End locations
def get_random_start(grid_width: int, grid_height: int, block_w: int, block_h: int) ->Block:
    """Returns a list containing start and end Blocks"""
    start_x = random.randint(0, grid_width)
    start_y = 0
    end_x = random.randint(0, grid_width)
    end_y = grid_height - 1

    start_block = Block(start_x, start_y, BlockDirections.North)

    return start_block

def check_block_exits(block: Block, block_list: List[Block]) -> None:
    direction_list = block.exit_directions.copy()
    for direction in direction_list:
        check_x, check_y = BlockDirections.get_x_y_in_direction(direction, block)

        for exit_block in block_list:
            if exit_block.grid_x == check_x and exit_block.grid_y == check_y:
                block.exit_directions.remove(direction)

def get_lowest_block(block_list: List[Block]):
    if len(block_list) == 0:
        return None

    lowest_block = block_list[0]

    for block in block_list:
        if block.grid_y > lowest_block.grid_y:
            lowest_block = block
    
    return lowest_block


def set_random_exits_and_get_blocks(block: Block, block_list: List[Block], grid_width: int, grid_height: int, exit_chance: float = 0.5) -> List[Block]:
    """Returns a list of valid random exits"""
    invalid_exits = [block.entry_direction]

    if block.grid_x == 0:
        invalid_exits.append(BlockDirections.West)
    if block.grid_x == grid_width - 1:
        invalid_exits.append(BlockDirections.East)
    if block.grid_y == 0:
        invalid_exits.append(BlockDirections.North)
    if block.grid_y == grid_height - 1:
        invalid_exits.append(BlockDirections.South)

    new_blocks = []
    number_exits = 0

    for direction in BlockDirections:
        if direction in invalid_exits:
            continue

        new_grid_x = block.grid_x
        new_grid_y = block.grid_y
        new_direction_entry = BlockDirections.get_opposite_direction(direction)

        if direction == BlockDirections.South:
            new_grid_y += 1
        if direction == BlockDirections.North:
            new_grid_y -= 1
        if direction == BlockDirections.East:
            new_grid_x += 1
        if direction == BlockDirections.West:
            new_grid_x -= 1
        
        new_block = Block(new_grid_x, new_grid_y, new_direction_entry)

        if (new_block not in block_list and random.randint(0,100) < (exit_chance * 100)):
            new_blocks.append(new_block)
            block.exit_directions.append(direction)
            number_exits += 1
    
    return new_blocks

# Generate a Maze
pixel_w, pixel_h = 1000, 1000
block_w, block_h = 10, 10
grid_w, grid_h = pixel_w // block_w, pixel_h // block_h

pixel_array = np.full((pixel_w, pixel_h, 3), [255, 255, 255], np.uint8)
start_block = get_random_start(grid_w, grid_h, block_w, block_h)
end_block = None

already_visited_blocks = []
blocks_to_explore = [start_block]
block_at_bottom = False

while not block_at_bottom:
    while blocks_to_explore:
        blocks_to_explore_previous = blocks_to_explore.copy()
        blocks_to_explore = []

        for block in blocks_to_explore_previous:
            invalid_blocks = already_visited_blocks.copy()
            invalid_blocks.extend(blocks_to_explore)

            blocks_to_explore.extend(set_random_exits_and_get_blocks(block, invalid_blocks, grid_w, grid_h))
            already_visited_blocks.append(block)
    

    lowest_block = get_lowest_block(already_visited_blocks)
    pixel_array = draw_block_walls(block, block_w, block_h, pixel_array)
    save_array_as_png("Output.png", pixel_array)

    if lowest_block.grid_y != grid_h - 1:
        lowest_block.exit_directions.append(BlockDirections.South)
        blocks_to_explore.append(lowest_block)
    else:
        end_block = lowest_block
        block_at_bottom = True

end_block.exit_directions.append(BlockDirections.South)        

for block in already_visited_blocks:
    pixel_array = fill_block(block, block_w, block_h, pixel_array, PATH_COLOR)
    pixel_array = draw_block_walls(block, block_w, block_h, pixel_array)

pixel_array = fill_block(start_block, block_w, block_h, pixel_array, START_BLOCK_COLOR)
pixel_array = fill_block(end_block, block_w, block_h, pixel_array, END_BLOCK_COLOR)

pixel_array = draw_block_walls(start_block, block_w, block_h, pixel_array)
pixel_array = draw_block_walls(end_block, block_w, block_h, pixel_array)

save_array_as_png("Output.png", pixel_array)

# center_block = Block(grid_w // 2, grid_h // 2, BlockDirections.East)

# pixel_array = draw_block_into_pixel_array(center_block, block_w, block_h, pixel_array)

# save_array_as_png("Output.png", pixel_array)


