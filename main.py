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


path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph = \
    get_initial_path(game_map)

draw_game(screen, game_map,
          pacman_pos, ghost_positions,
          food_positions, super_fruit_pos,
          ghost_hunter=False)
pygame.display.flip()
pygame.time.wait(50) # Pause to show initial state

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic
    pacman_pos, ghost_positions, food_positions, super_fruit_pos, ghost_hunter = update_game(graph, pacman_pos, ghost_positions, food_positions, super_fruit_pos)

    # Draw the game
    draw_game(screen, game_map, pacman_pos, ghost_positions, food_positions, super_fruit_pos, ghost_hunter)

    # Refresh display
    pygame.display.flip()
    
    # Termination checks
    if not food_positions:
        print("Level complete.")
        running = False
        outcome = "level_complete"
    elif pacman_pos in ghost_positions and not ghost_hunter:
        print("Death.")
        running = False
        outcome = "death"

    clock.tick(FPS)

pygame.quit()