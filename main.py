from utils.map import WordMaze
import time
import argparse

def parseargs() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--grid_width", help="The number of blocks wide to make the maze.", type=int, default=20)
    arg_parser.add_argument("--grid_height", help="The number of blocks high to make the maze.", type=int, default=20)
    arg_parser.add_argument("--pixel_width", help="The number of pixels wide for a block in the maze.", type=int, default=20)
    arg_parser.add_argument("--pixel_height", help="The number of pixels hight for a block in the maze.", type=int, default=20)
    arg_parser.add_argument("--num_to_generate", help="How many would you like to generate?", type=int, default=1)
    arg_parser.add_argument("--solution", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--direction_display", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--num_exit_display", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--show_path_generation", help="Save a GIF showing how the paths were generated.", action="store_true", default=False)
    arg_parser.add_argument("--show_letter_placement", help="Save a GIF showing how the letters were placed.", action="store_true", default=False)
    arg_parser.add_argument("--filename", help="What to name the output maze.", type=str, default="Output_Maze.png")
    arg_parser.add_argument("--word", help="What word to guide the solver.", type=str, default="Hello")

    return arg_parser.parse_known_args()

def test_maze_inputs():
    words = ["Hello", "Random", "Testing", "Maze", "Generation"]
    grid_widths = [(20, 20), (40, 40), (80, 80), (160, 160)]

    for word in words:
        for width in grid_widths:
            ns = argparse.Namespace(word=word, grid_width=width[0], grid_height=width[1], pixel_width=20, pixel_height=20)
            yield ns

if __name__ == "__main__":
    args, _ = parseargs()

    for test_input in test_maze_inputs():
        print(f"testing {test_input}")
        start_time = time.perf_counter()
        WordMaze(test_input.word, test_input.grid_width, test_input.grid_height, test_input.pixel_width, test_input.pixel_height)
        stop_time = time.perf_counter()
        print(stop_time - start_time)



    # maze_generation_time = timeit.timeit(WordMaze(args.word, args.grid_width, args.grid_height, args.pixel_width, args.pixel_height, args=args), number=20)
    # maze = WordMaze(args.word, args.grid_width, args.grid_height, args.pixel_width, args.pixel_height, args=args)
    # maze.save_image(args.filename.split(".")[0] + "_" + str(i) + ".png")


    
