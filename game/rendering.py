import pygame
from game.settings import BLACK, BLUE, YELLOW, GREEN, PURPLE, WHITE, TILE_SIZE
from game.score_tracker import get_score

def draw_game(screen, game_map, pacman_pos, ghost_positions, food_positions, super_fruit_pos, ghost_hunter):
    """ Draws game elements on the screen """

    screen.fill(BLACK)  # Clear the screen

    # Draw walls and objects
    for row in range(len(game_map)):
        for col in range(len(game_map[row])):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            if game_map[row][col] == "#":
                pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
            # elif game_map[row][col] == "F":
            #     pygame.draw.circle(screen, PURPLE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)

    # Draw food
    for food in food_positions:
        x, y = food[1] * TILE_SIZE, food[0] * TILE_SIZE
        pygame.draw.circle(screen, GREEN, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 8)

    # Draw ghosts
    for ghost in ghost_positions:
        x, y = ghost[1] * TILE_SIZE, ghost[0] * TILE_SIZE
        pygame.draw.circle(screen, WHITE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)
        
    # Draw ghosts
    if super_fruit_pos:
        x, y = super_fruit_pos[1] * TILE_SIZE, super_fruit_pos[0] * TILE_SIZE
        
        pygame.draw.circle(screen, PURPLE, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)

    # Draw Pac-Man
    x, y = pacman_pos[1] * TILE_SIZE, pacman_pos[0] * TILE_SIZE

    font = pygame.font.SysFont(None, 24)
    score_surf = font.render(f"Score: {get_score()}", True, WHITE)
    screen.blit(score_surf, (10, 4))

    mode = "HUNTER" if ghost_hunter else "NORMAL"
    mode_surf = font.render(mode, True, WHITE)
    screen.blit(mode_surf, (10, 24))
    pygame.draw.circle(screen, YELLOW, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)
