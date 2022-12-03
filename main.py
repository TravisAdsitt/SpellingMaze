from utils.map import Maze, WordMaze
import time
import argparse
from reportlab.pdfgen import canvas

def parseargs() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--grid_width", help="The number of blocks wide to make the maze.", type=int, default=20)
    arg_parser.add_argument("--grid_height", help="The number of blocks high to make the maze.", type=int, default=20)
    arg_parser.add_argument("--pixel_width", help="The number of pixels wide for a block in the maze.", type=int, default=20)
    arg_parser.add_argument("--pixel_height", help="The number of pixels hight for a block in the maze.", type=int, default=20)
    arg_parser.add_argument("--num_to_generate", help="How many would you like to generate?", type=int, default=1)
    arg_parser.add_argument("--pdf", help="Generate a pdf version of the mazes", action="store_true", default=False)
    arg_parser.add_argument("--solution", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--direction_display", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--num_exit_display", help="Paint and save the solution path", action="store_true", default=False)
    arg_parser.add_argument("--show_path_generation", help="Save a GIF showing how the paths were generated.", action="store_true", default=False)
    arg_parser.add_argument("--filename", help="What to name the output maze.", type=str, default="Output_Maze.png")
    arg_parser.add_argument("--word", help="What word to guide the solver.", type=str, default="Hello")

    return arg_parser.parse_args()

def save_pdf(file_location: str, width: int, height: int):
    my_canvas = canvas.Canvas(file_location.split(".")[0] + ".pdf")
    my_canvas.drawImage(file_location, 10, 10, width, height)
    my_canvas.save()

if __name__ == "__main__":
    args = parseargs()

    for i in range(args.num_to_generate):
        maze = WordMaze(args.word, args.grid_width, args.grid_height, args.pixel_width, args.pixel_height, args=args)
        maze.save_image(args.filename.split(".")[0] + "_" + str(i) + ".png")

        if args.direction_display:
            maze.map.draw_block_directions()
            maze.map.draw()
            maze.save_image(args.filename.split(".")[0] + "_" + str(i) + "_path_directions.png")

        if args.num_exit_display:
            maze.map.draw_block_exit_count()
            maze.map.draw()
            maze.save_image(args.filename.split(".")[0] + "_" + str(i) + "_num_exit_display.png")

        if args.solution:
            maze.solve_maze(True)
            maze.map.draw()
            maze.save_image(args.filename.split(".")[0] + "_" + str(i) + "_solution.png")

        if args.pdf:
            save_pdf(args.filename, args.grid_width * args.pixel_width, args.grid_height * args.pixel_height)


    
