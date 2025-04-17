import pygame
from game.settings import WIDTH, HEIGHT, FPS
from game.game_logic import update_game
from game.rendering import draw_game
from maps.level1 import game_map
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
    pacman_pos, ghost_positions, food_positions, super_fruit_pos, running = update_game(graph, pacman_pos, ghost_positions, food_positions, super_fruit_pos, running)

    # Draw the game
    draw_game(screen, game_map, pacman_pos, ghost_positions, food_positions, super_fruit_pos)

    # Refresh display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()