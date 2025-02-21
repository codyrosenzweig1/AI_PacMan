# import pygame
# import random
# from Small_Projects.Pacman.AI.search import bfs, build_graph, smarter_a_star

# Set up constants
# WIDTH, HEIGHT = 600, 600
# FPS = 20
# ROWS, COLS = 15, 15  # Grid size (15x15 tiles)
# TILE_SIZE = 40 # Grid square will be 40 x 40 pixels

# # Colors
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# BLUE = (0, 0, 255)  # Walls
# YELLOW = (255, 255, 0)  # Pac-Man
# GREEN = (0, 255, 0)  # Food
# PURPLE = (160, 32, 240)  # Power-up fruit
# RED = (255, 0, 0) # Path visualisation
# LIGHT_BLUE = (173, 216, 230)  # BFS expansion

# # Define the grid-based map
# game_map = [
#     "###############",
#     "#P..........#.#",
#     "#.#.#####.#.#.#",
#     "#.#.#...#.#.#.#",
#     "#.#.#.#.#.#.#.#",
#     "#...#.#.#.#...#",
#     "###.#.#.#.#####",
#     "#...#.....#...#",
#     "#.#.#######.#.#",
#     "#.#.........#.#",
#     "#.#.#######.#.#",
#     "#.#...F.....#.#",
#     "#.###########.#",
#     "#........G....#",
#     "###############"
# ]


# # Initialise Pygame
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("AI Pac-Man")
# clock = pygame.time.Clock()

# # Convert the maze into an adjacency list
# graph, pacman_pos, _ = build_graph(game_map)

# # Extract food and ghost positions
# # Extract food, ghost, and super fruit positions
# food_positions = {(row, col) for row in range(ROWS) for col in range(COLS) if game_map[row][col] == "."}
# super_fruit_pos = next(((row, col) for row in range(ROWS) for col in range(COLS) if game_map[row][col] == "F"), None)
# ghost_positions = [(row, col) for row in range(ROWS) for col in range(COLS) if game_map[row][col] == "G"]

# # Run smarter A* search for Pac-Man's initial path
# # Run A* search for Pac-Man's new goal (super fruit)
# if super_fruit_pos:
#     path = smarter_a_star(graph, pacman_pos, {super_fruit_pos}, set(ghost_positions))
# else:
#     path = []
    
# print("Generated Path:", path)
# path_index = 0
    
# # Function to move ghosts around randomly to begin with
# def move_ghosts(graph, ghosts):
#     new_positions = []
#     for ghost in ghosts:
#         possible_moves = graph[ghost]  # Get all valid moves for the ghost
#         if possible_moves:
#             new_positions.append(random.choice(possible_moves))  # Pick a random move
#         else:
#             new_positions.append(ghost)  # Stay in place if no valid move
#     return new_positions

# # Function to update Pac-Man's movement
# def update_pacman():
#     global pacman_pos, path_index

#     if path and path_index < len(path):
#         print("Moving Pac Man to:", path[path_index])
#         pacman_pos = path[path_index] # Move Pac-Man to the next tile
#         path_index += 1  # Advance along the path

# # Main game loop
# running = True
# while running:
#     # Handle events
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT: # If user closes the window
#             running = False
            
#     # Ghost movement
#     ghost_positions = move_ghosts(graph, ghost_positions)
            
#     # Pac-Man movement
#     update_pacman()

#     # Fill screen with black background
#     screen.fill(BLACK)
    
#     # Draw the grid-based map
#     for row in range(ROWS):
#         for col in range(COLS):
#             tile = game_map[row][col]
#             x, y = col * TILE_SIZE, row * TILE_SIZE # Finds the starting pixel of the tile (120, 80)
            
#             if tile == "#":  # Draw walls
#                 pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE)) # Then draws the corresponding shape using the tile size
#             elif tile == "F":  # Draw super fruit
#                 pygame.draw.circle(screen, PURPLE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)
            
#             #elif tile == "P":  # Draw Pac-Man
#              #   pygame.draw.circle(screen, YELLOW, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3) # Moves the centre of the circle (Pac-Man) to be middle of the tile
            
            
#     # Draw food
#     for food in food_positions:
#         x, y = food[1] * TILE_SIZE, food[0] * TILE_SIZE
#         pygame.draw.circle(screen, GREEN, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 8) # The last param is the radius of the circle

#     # Draw ghosts
#     for ghost in ghost_positions:
#         ghost_x, ghost_y = ghost[1] * TILE_SIZE, ghost[0] * TILE_SIZE
#         pygame.draw.circle(screen, WHITE, (ghost_x + TILE_SIZE // 2, ghost_y + TILE_SIZE // 2), TILE_SIZE // 3)
        
#     # Draw Pac-Man at new position
#     pac_x, pac_y = pacman_pos[1] * TILE_SIZE, pacman_pos[0] * TILE_SIZE
#     pygame.draw.circle(screen, YELLOW, (pac_x + TILE_SIZE // 2, pac_y + TILE_SIZE // 2), TILE_SIZE // 3)
        
#     # Update display
#     pygame.display.flip()
#     clock.tick(FPS) # Control movement speed
    
# # Quit pygame properly
# pygame.quit()





import pygame
from game.settings import WIDTH, HEIGHT, FPS
from game.game_logic import update_game
from game.rendering import draw_game
from maps.level2 import game_map
from ai.path_manager import get_exploration_path, get_initial_path

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Pac-Man")
clock = pygame.time.Clock()

# Get initial path for Pac-Man
path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph = get_initial_path(game_map)

# print("path", path)
# print("PacMan Position:", pacman_pos)
# print("ghost positions:", ghost_positions)
# print("food positions:", food_positions)
# print("super fruit positions", super_fruit_pos)
# print("Graph;", graph)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic
    pacman_pos, ghost_positions, food_positions, super_fruit_pos = update_game(graph, pacman_pos, ghost_positions, food_positions, super_fruit_pos)

    # Draw the game
    draw_game(screen, game_map, pacman_pos, ghost_positions, food_positions, super_fruit_pos)

    # Refresh display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()