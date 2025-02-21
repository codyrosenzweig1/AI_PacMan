# Set up constants
WIDTH, HEIGHT = 600, 600
FPS = 3
ROWS, COLS = 15, 15  # Grid size (15x15 tiles)
TILE_SIZE = 40 # Grid square will be 40 x 40 pixels

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)  # Walls
YELLOW = (255, 255, 0)  # Pac-Man
GREEN = (0, 255, 0)  # Food
PURPLE = (160, 32, 240)  # Power-up fruit
RED = (255, 0, 0) # Path visualisation
LIGHT_BLUE = (173, 216, 230)  # BFS expansion

# Define the grid-based map
game_map = [
    "###############",
    "#P..........#.#",
    "#.#.#####.#.#.#",
    "#.#.#...#.#.#.#",
    "#.#.#.#.#.#.#.#",
    "#...#.#.#.#...#",
    "###.#.#.#.#####",
    "#...#.....#...#",
    "#.#.#######.#.#",
    "#.#.........#.#",
    "#.#.#######.#.#",
    "#.#...F.....#.#",
    "#.###########.#",
    "#........G....#",
    "###############"
]

# Initial pacman position in path
PATH_INDEX = 0