from ai.search import smarter_a_star, build_graph
from game.settings import TILE_SIZE
from maps.level1 import game_map
from game.game_logic import move_ghosts

def get_initial_path(game_map):
    """ Initializes the game and gets Pac-Man's starting path """
    graph, pacman_pos, _ = build_graph(game_map)

    # Extract important game objects
    food_positions = {(r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "."}
    super_fruit_pos = next(((r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "F"), None)
    ghost_positions = [(r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "G"]

    # Get initial path to super fruit
    path = smarter_a_star(graph, pacman_pos, {super_fruit_pos}, set(ghost_positions)) if super_fruit_pos else []

    return path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph
