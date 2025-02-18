import pygame
from search import bfs

# Initialise Pygame
pygame.init()

# Set up constants
WIDTH, HEIGHT = 600, 600
FPS = 20
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

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Pac-Man")

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
    "#.#.........#.#",
    "#.###########.#",
    "#........F....#",
    "###############"
]

# Find Pacman and food positions
def find_position(game_map):
    pacman_pos = None
    food_pos = None
    for row in range(len(game_map)):
        for col in range(len(game_map[row])):
            if game_map[row][col] == "P":
                pacman_pos = (row, col)
            elif game_map[row][col] == "F":
                food_pos = (row, col) # Take the first food found
    return pacman_pos, food_pos

pacman_pos, food_pos = find_position(game_map)

# Find the shortest path using bfs
if pacman_pos and food_pos:
    path, bfs_exploration = bfs(game_map, pacman_pos, food_pos) # get the shortest path and search order
    path_index = 0 # Track Pac-Man's progress along the path
    exploration_index = 0 # Track BFS's expansion
else:
    path, bfs_exploration = [], []

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # If user closes the window
            running = False
            
    # Animate BFS expansion before PAC-Man moves
    if exploration_index < len(bfs_exploration):
        current_explored = bfs_exploration[exploration_index]
        exploration_index += 1
            
    # Move Pac-Man along the path after bfs is visualised
    elif path and path_index < len(path):
        pacman_pos = path[path_index]
        path_index += 1
    
    # Fill screen with black background
    screen.fill(BLACK)
    
    # Draw the grid-based map
    for row in range(ROWS):
        for col in range(COLS):
            tile = game_map[row][col]
            x, y = col * TILE_SIZE, row * TILE_SIZE # Finds the starting pixel of the tile (120, 80)
            
            if tile == "#":  # Draw walls
                pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE)) # Then draws the corresponding shape using the tile size
            elif tile == "P":  # Draw Pac-Man
                pygame.draw.circle(screen, YELLOW, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3) # Moves the centre of the circle (Pac-Man) to be middle of the tile
            elif tile == "F":  # Draw food pellets
                pygame.draw.circle(screen, PURPLE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 8) # The last param is the radius of the circle

    # Draw BFS expansion (light blue)
    for i in range(exploration_index):
        x, y = bfs_exploration[i][1] * TILE_SIZE, bfs_exploration[i][0] * TILE_SIZE
        pygame.draw.rect(screen, LIGHT_BLUE, (x, y, TILE_SIZE, TILE_SIZE))

    # Draw BFS path (visualisation) (red)
    for pos in path:
        x, y = pos[1] * TILE_SIZE, pos[0] * TILE_SIZE
        pygame.draw.rect(screen, RED, (x, y, TILE_SIZE, TILE_SIZE), 2)
        
    # Draw Pac-Man at new position
    pac_x, pac_y = pacman_pos[1] * TILE_SIZE, pacman_pos[0] * TILE_SIZE
    pygame.draw.circle(screen, YELLOW, (pac_x * TILE_SIZE // 2, pac_y * TILE_SIZE // 2), TILE_SIZE // 3)
        
    # Update display
    pygame.display.flip()
    clock.tick(FPS) # Control movement speed
    
# Quit pygame properly
pygame.quit()