from ai.search import smarter_a_star, build_graph
from game.settings import TILE_SIZE
from maps.level1 import game_map

def get_initial_path(game_map):
    """ Initializes the game and gets Pac-Man's starting path """
    graph, pacman_pos, _ = build_graph(game_map)

    # Extract important game objects
    food_positions = {(r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "."}
    super_fruit_pos = next(((r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "F"), None)
    ghost_positions = [(r, c) for r in range(len(game_map)) for c in range(len(game_map[0])) if game_map[r][c] == "G"]

    # Get initial path to super fruit
    path = smarter_a_star(graph, pacman_pos, {super_fruit_pos}, set(ghost_positions), game_map) if super_fruit_pos else []

    return path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph

def find_frontiers(graph, visited):
    """
    Identifies unexplored tiles (frontiers) in the maze.
    A frontier is a tile that Pac-Man has not visited yet.
    """
    frontiers = set()
    
    for node in graph:  # Iterate through all tiles in the graph
        if node not in visited:
            frontiers.add(node)  # Add unexplored tiles as frontiers

    return frontiers

def get_exploration_path(graph, pacman_pos, visited, ghost_positions, super_fruit_pos):
    """
    Determines the safest path to an unexplored frontier while avoiding ghosts.
    """
    # from game.game_logic import move_ghosts
    
    frontiers = find_frontiers(graph, visited)
    if not frontiers:
        return []  # If no frontiers left, the maze is fully explored

    # Select the closest and safest frontier
    safest_frontier = None
    min_distance = float('inf')

    for frontier in frontiers:
        if frontier not in ghost_positions:  # Ensure we do not pick a ghost tile
            distance = abs(frontier[0] - pacman_pos[0]) + abs(frontier[1] - pacman_pos[1])
            if distance < min_distance:
                min_distance = distance
                safest_frontier = frontier
                # print("Safest frontier;", safest_frontier)

    # Use A* search to reach the safest unexplored tile
    if safest_frontier:
        return smarter_a_star(graph, pacman_pos, {safest_frontier}, ghost_positions, game_map)
    
    return []