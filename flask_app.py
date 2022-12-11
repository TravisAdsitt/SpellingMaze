# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, send_file
from main import parseargs

from utils.map import WordMaze

app = Flask(__name__)

def generate_maze(word: str) -> str:
    # Determine an arbitrary square Grid Width and Height
    grid_width = grid_height = 25
    block_width = block_height = 20
    word = word.lower()
    # Generate the maze
    maze = WordMaze(word, grid_width, grid_height, block_width, block_height, args=parseargs())
    # Save the maze to a file
    filename = f"static/{word}.png"
    maze.save_image(filename)
    # Return where to find the maze
    return '/' + filename

@app.route('/')
def index():
    return render_template("base.html")

@app.route('/maze', methods=["GET"])
def get_maze():
    if request.method == 'GET':
        if not request.args.get('word'):
            return "Invalid Input"

        word = request.args.get('word')

        return generate_maze(word)

    return 'Nothing Here'

if __name__ == '__main__':
    app.run(debug=True)