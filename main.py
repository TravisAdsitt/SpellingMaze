from utils.drawable import COLOR_RED
from utils.map import Maze
import time


if __name__ == "__main__":
    for i in range(1, 100):
        generation_times = []
        save_times = []
        for j in range(3):
            generation_start = time.time()
            maze = Maze(i,i)
            maze.generate_maze()
            generation_times.append(time.time() - generation_start)
            save_start = time.time()
            maze.save_image(f"Output_maze_{i}x{i}_{j + 1}.png")
            save_times.append(time.time() - save_start)
        average_gen = sum(generation_times) / len(generation_times)
        average_save = sum(save_times) / len(save_times)

        print(f"A {i}x{i} maze took {average_gen}s to generate and {average_save}s to save on an RPI4 8GB.")

    
