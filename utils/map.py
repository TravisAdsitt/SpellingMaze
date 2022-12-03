from enum import Enum
import string
from utils.drawable import COLOR_BLACK, COLOR_GRAY, COLOR_GREEN, COLOR_RED, COLOR_WHITE, Drawable2D, Color
from typing import List, Tuple
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont

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
        self.pallete.add("background_color", COLOR_WHITE)

        self.exit_directions = exit_directions if exit_directions else []
        self.entry_direction = entry_direction
        self.explored = False
        self.letter = None
        self._has_changed = True

    @property
    def letter(self):
        if not hasattr(self, "_letter"):
            self._letter = None
        
        return self._letter
    
    @letter.setter
    def letter(self, new_letter: str):
        if new_letter and len(new_letter) > 1:
            return
        
        self._letter = new_letter
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
    
    @property
    def is_multi_exit(self):
        return bool(len(self.exit_directions) > 1)

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
        
        if self.letter:
            font = 'data/Arial.ttf'
            pil_font = ImageFont.truetype(f"{font}", size=self.width, encoding="unic")
            text_width, text_height = pil_font.getsize(self.letter)

            canvas = Image.fromarray(np.array(self.color_array).astype(np.uint8))
            draw = ImageDraw.Draw(canvas)
            offset = ((self.width - text_width) // 2, (self.width - text_height) // 2)
            black = "#000000"
            draw.text(offset, self.letter, font=pil_font, fill=black)
            self.color_array = np.asarray(canvas)
            self.color_array.reshape((self.height, self.width, 3))
            self.color_array = self.color_array.tolist()

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

    def clean_all_blocks(self):
        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                self.clean_block_relationships(self.block_grid[y][x])
                self.block_grid[y][x]._has_changed = True

    def get_all_explored_blocks(self) -> List[Block]:
        ret_list = []

        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                if self.block_grid[y][x].explored:
                    ret_list.append(self.block_grid[y][x])
        
        return ret_list

    def get_start_block(self):
        return random.choice(self.block_grid[0])
    
    def clean_block_relationships(self, block: Block):
        block.exit_directions = [*set(block.exit_directions)]

        if block.entry_direction in block.exit_directions:
            block.exit_directions.remove(block.entry_direction)

        for direction, check_block in self.get_blocks_in_all_directions(block, False):
            check_relative_direction = GridDirection.get_opposite_direction(direction)

            # Check Block has no relationship to this block
            if direction != block.entry_direction and direction not in block.exit_directions:
                # Make sure the other block isn't exiting or entering from our direction
                if check_relative_direction == check_block.entry_direction:
                    check_block.entry_direction = None
                if check_relative_direction in check_block.exit_directions:
                    check_block.exit_directions.remove(check_relative_direction)
            # Ensure our exit is actually the entry
            elif direction in block.exit_directions:
                if check_block.entry_direction != check_relative_direction:
                    block.exit_directions.remove(direction)

    def get_all_junctions(self, ignore_cache: bool = False):
        if not hasattr(self, "_junction_starts") or ignore_cache:
            self._junction_starts = []
        else:
            return self._junction_starts

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                curr_block = self.block_grid[y][x]

                if len(curr_block.exit_directions) < 2:
                    continue
                
                self._junction_starts.append(curr_block)
        
        return self._junction_starts

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

    def get_blocks_relative_direction(self, block_from: Block, block_to: Block) -> GridDirection or None:
        for direction, block in self.get_blocks_in_all_directions(block_from):
            if block == block_to:
                return direction
        
        return None

    def get_blocks_in_all_directions(self, block: Block, ignore_explored: bool = True) -> List[Tuple[GridDirection, Block]]:
        ret_val = []

        for direction in GridDirection:
            curr_block = self.get_block_in_direction(block, direction, ignore_explored)
            if curr_block:
                ret_val.append((direction, curr_block))
        
        return ret_val

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

    def draw_block_exit_count(self):
        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                curr_block = self.block_grid[y][x]
                curr_block.letter = f"{len(curr_block.exit_directions)}"

    def draw_block_directions(self):
        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                curr_block = self.block_grid[y][x]
                entry_direction = curr_block.entry_direction

                if entry_direction == GridDirection.North:
                    curr_block.letter = "v"
                elif entry_direction == GridDirection.South:
                    curr_block.letter = "^"
                elif entry_direction == GridDirection.East:
                    curr_block.letter = "<"
                elif entry_direction == GridDirection.West:
                    curr_block.letter = ">"
    
    def draw(self) -> List[List[Color]]:
        for y in range(len(self.block_grid)):
            for x in range(len(self.block_grid[y])):
                self.clean_block_relationships(self.block_grid[y][x])
                block_color_data = self.block_grid[y][x].draw()
                if block_color_data:
                    self.draw_portion(x * self.block_width, y * self.block_height, block_color_data)
        
        return self.color_array

class Path:
    def __init__(self, map: Map, start_block: Block or List[Block], min_path_length: int = 1):
        self.map = map
        self.blocks = [start_block] if isinstance(start_block, Block) else start_block
        self.min_path_length = min_path_length

        self.complete = False

    def clean_path_walls(self):
        for block in self.blocks:
            self.map.clean_block_relationships(block)

    def set_random_exits(self, block: Block, chance: float = 0.6) -> List[Block]:
        ret_val = list()

        for direction, check_block in self.map.get_blocks_in_all_directions(block):
            if check_block and random.randint(1, 100) < int(chance * 100):
                block.exit_directions.append(direction)
                check_block.entry_direction = GridDirection.get_opposite_direction(direction)
                ret_val.append(check_block)
        
        return ret_val

    def get_all_connected_blocks(self):
        if len(self.blocks):
            return []
        
        explored_blocks = [self.blocks[0]]
        blocks_to_explore = []

        for direction in explored_blocks[0].exit_directions:
            blocks_to_explore.append(self.map.get_block_in_direction(explored_blocks[0], direction))
        blocks_to_explore.append(self.map.get_block_in_direction(explored_blocks[0], explored_blocks[0].entry_direction))

        while blocks_to_explore:
            remove_blocks = []
            add_blocks = []
            for block in blocks_to_explore:
                if block not in explored_blocks:
                    explored_blocks.append(block)

                remove_blocks.append(block)

                for direction in block.exit_directions:
                    exit_block = self.map.get_block_in_direction(block, direction)
                    if exit_block not in blocks_to_explore and exit_block not in add_blocks and entry_block not in explored_blocks:
                        add_blocks.append(exit_block)

                if block.entry_direction:
                    entry_block = self.map.get_block_in_direction(block, block.entry_direction)
                    if entry_block not in blocks_to_explore and entry_block not in add_blocks and entry_block not in explored_blocks:
                        add_blocks.append()

            for block in remove_blocks:
                blocks_to_explore.remove(block)
            for block in add_blocks:
                blocks_to_explore.add(block)
        
        return explored_blocks
        
    def step_path(self) -> List[Block]:
        ret_blocks = []

        if self.complete:
            return ret_blocks

        exit_block_list = [self.blocks[-1]]

        while exit_block_list:
            current_block = random.choice(exit_block_list)
            exit_block_list.remove(current_block)

            if current_block in ret_blocks:
                ret_blocks.remove(current_block)

            current_block.explored = True
            ret_blocks.extend(exit_block_list)

            exit_block_list = self.set_random_exits(current_block)
            self.blocks.append(current_block)

        self.complete = True

        return ret_blocks

class Maze:
    def __init__(self, grid_width: int, grid_height: int, block_width: int, block_height: int) -> Tuple[int, Block]:
        self.map = Map(grid_width, grid_height, block_width, block_height)
        self.generate_maze()
        self.solve_maze()

    def get_lowest_block(self):
        for y in range(self.map.grid_height - 1, -1, -1):
            explored_blocks = [block.explored for block in self.map.block_grid[y]]
            if any(explored_blocks):
                explored_low_blocks = [block for block in self.map.block_grid[y] if block.explored]

                return (y, random.choice(explored_low_blocks))
        
        return None

    def generate_paths(self, start_block: Block):
        possible_path_starts = [start_block]

        while possible_path_starts:
            current_start = random.choice(possible_path_starts)
            possible_path_starts.remove(current_start)

            if current_start.explored:
                continue

            path = Path(self.map, current_start)
            while not path.complete:
                possible_path_starts.extend(path.step_path())

    def generate_maze(self):
        self.map_start = self.map.get_start_block()
        self.map_end = None

        self.map_start.entry_direction = GridDirection.North

        new_start = self.map_start
        while not self.map_end:
            self.generate_paths(new_start)
            
            y, lowest_block = self.get_lowest_block()
            lowest_block.exit_directions.append(GridDirection.South)

            if y == self.map.grid_height - 1:
                self.map_end = lowest_block
            else:
                new_start = self.map.get_block_in_direction(lowest_block, GridDirection.South)
                new_start.entry_direction = GridDirection.North

        self.map.draw()
    
    def solve_maze(self, paint_path: bool = False):
        start = self.map_start
        self.solution_path = None
        exploring_paths = [Path(self.map, start)]
        while not self.solution_path and exploring_paths:
            temp_exploring_paths = exploring_paths
            for path in temp_exploring_paths:
                curr_block = path.blocks[-1]

                if len(curr_block.exit_directions) == 0 and curr_block != self.map_end:
                    exploring_paths.remove(path)
                    continue
                elif curr_block == self.map_end:
                    self.solution_path = path
                    break
                if curr_block.is_multi_exit:
                    for direction in curr_block.exit_directions:
                        blocks = path.blocks.copy()
                        directed_block = self.map.get_block_in_direction(curr_block, direction, False)
                        blocks.append(self.map.get_block_in_direction(curr_block, direction, False))
                        
                        exploring_paths.append(Path(self.map, blocks))
                    exploring_paths.remove(path)
                else:
                    directed_block = self.map.get_block_in_direction(curr_block, curr_block.exit_directions[0], False)
                    path.blocks.append(directed_block)
            exploring_paths = temp_exploring_paths
        
        if paint_path:
            for block in self.solution_path.blocks:
                block.pallete.background_color = COLOR_GREEN
                block._has_changed = True
        
        self.map.draw()

    def save_image(self, filename: str):
        return self.map.save_array_as_png(filename)
         
      
class WordMaze(Maze):
    def __init__(self, word: str, grid_width: int = 20, grid_height: int = 20, block_width: int = 20, block_height: int = 20):
        if not word.isalpha():
            raise ValueError("Word contains invalid characters, only alphabet characters are allowed.")

        super().__init__(grid_width, grid_height, block_width, block_height)
        self.word = word
        self.map.clean_all_blocks()
        self.apply_word()
        self.map.draw()

    def close_and_unexplore_connected_blocks(self, block: Block):
        if not block:
            return

        # Close off the entry
        exit_block = self.map.get_block_in_direction(block, block.entry_direction, False)
        exit_block.exit_directions.remove(GridDirection.get_opposite_direction(block.entry_direction))

        blocks_to_clear = [block]

        while blocks_to_clear:
            curr_block = blocks_to_clear[0]
            curr_block.entry_direction = None
            curr_block.explored = False
            blocks_to_clear.remove(curr_block)

            for direction in curr_block.exit_directions:
                next_block = self.map.get_block_in_direction(curr_block, direction, False)
                blocks_to_clear.append(next_block)
            
            curr_block.exit_directions = []

    def place_letter_in_exit_blocks(self, block_with_exits: Block, word_index: int = None):
        invalid_letters = [l for l in string.ascii_letters if l not in self.word]

        for direction in block_with_exits.exit_directions:
            letter_block = self.map.get_block_in_direction(block_with_exits, direction, False)

            if not letter_block:
                block_with_exits.exit_directions.remove(direction)
                continue

            if letter_block in self.solution_path.blocks and word_index:
                letter_block.letter = self.word[word_index]
            else:
                letter_block.letter = random.choice(invalid_letters)

    def apply_word(self):
        exit_count = len(self.word)
        junctions = self.map.get_all_junctions()
        solution_junctions = []

        for start_block in junctions:
            if start_block in self.solution_path.blocks:
                solution_junctions.append(start_block)
        
        if len(solution_junctions) < exit_count - 1:
            raise IndexError("Not enough exit points to write word!")
        
        selected_junctions = []

        # Select some junctions for our words letters
        while len(selected_junctions) < len(self.word):
            next_chosen_block = random.choice(solution_junctions)
            if next_chosen_block not in selected_junctions:
                selected_junctions.append(next_chosen_block)

        # Close off and unexplore all other junctions
        for block in solution_junctions:
            if block in self.solution_path.blocks and block not in selected_junctions:
                for direction in block.exit_directions:
                    next_block = self.map.get_block_in_direction(block, direction, False)
                    if next_block not in self.solution_path.blocks:
                        self.close_and_unexplore_connected_blocks(next_block)

        # Reopen paths for unexplored areas on valid routes
        past_end_count = -1
        all_explored_blocks = self.map.get_all_explored_blocks()
        all_explored_end_path_blocks = [block for block in all_explored_blocks if len(block.exit_directions) == 0]
        new_end_count = len(all_explored_end_path_blocks)
        while past_end_count != new_end_count:
            past_end_count = new_end_count

            for block in all_explored_end_path_blocks:
                unexplored_blocks_around = self.map.get_blocks_in_all_directions(block)

                if unexplored_blocks_around:
                    direction, to_block = random.choice(unexplored_blocks_around)
                    if direction not in block.exit_directions:
                        block.exit_directions.append(direction)
                        to_block.entry_direction = GridDirection.get_opposite_direction(direction)
                        self.generate_paths(to_block)

            all_explored_blocks = self.map.get_all_explored_blocks()
            all_explored_end_path_blocks = [block for block in all_explored_blocks if len(block.exit_directions) == 0]
            new_end_count = len(all_explored_end_path_blocks)
        
        # Apply random invalid letters to all other junctions
        for block in self.map.get_all_junctions(ignore_cache=True):
            if block not in selected_junctions:
                self.place_letter_in_exit_blocks(block)
                
        exit_num = 0
        for block in self.solution_path.blocks:
            if block in selected_junctions:
                self.place_letter_in_exit_blocks(block, exit_num)
                exit_num += 1
            



        


            

            
        



