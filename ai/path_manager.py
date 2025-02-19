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

def get_exploration_path(graph, pacman_pos, visited, ghost_positions, food_positions, super_fruit_pos=None):
    """
    Determines the safest path to an unexplored frontier while avoiding ghosts.
    """
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

from ai.search import a_star

def escape_path(graph, pacman_pos, ghost_positions):
    """
    Uses a modified A* search where tiles near ghosts have higher movement costs.
    Ensures Pac-Man prioritizes paths that avoid danger instead of just taking the shortest path.
    """
    danger_map = {}

    # Assign dynamic weights to each tile based on proximity to ghosts
    for ghost in ghost_positions:
        for tile in graph.keys():  # Iterate over all valid tiles in the graph
            if tile == ghost:
                danger_map[tile] = float('inf')  # Ghost location is deadly
            else:
                ghost_distance = len(a_star(graph, tile, ghost))  # Use real movement distance

                # Assign weights: Closer tiles to ghosts have higher penalties
                if ghost_distance == 1:
                    danger_map[tile] = 100  # Immediate danger
                elif ghost_distance == 2:
                    danger_map[tile] = 50  # High risk
                elif ghost_distance <= 4:
                    danger_map[tile] = 20  # Moderate risk
                else:
                    danger_map[tile] = 1  # Low risk, normal movement

    # Modify A* to factor in danger weights
    def weighted_heuristic(tile, goal):
        return len(a_star(graph, tile, goal)) + danger_map.get(tile, 0)

    # Find the safest tile (furthest from all ghosts)
    safe_zones = [tile for tile in graph if tile not in danger_map or danger_map[tile] < 20]

    if not safe_zones:
        return []  # No escape route available

    # Pick the safest tile that is farthest from ghosts
    best_escape_tile = max(safe_zones, key=lambda tile: min(len(a_star(graph, tile, ghost)) for ghost in ghost_positions))

    # Compute and return the best path to escape
    return a_star(graph, pacman_pos, best_escape_tile)

