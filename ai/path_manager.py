from ai.search import smarter_a_star, build_graph, compute_partial_mst
from game.settings import TILE_SIZE
from maps.level1 import game_map
import heapq
from heapq import heappop, heappush  # Min-heap for priority queue

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
            # distance = abs(frontier[0] - pacman_pos[0]) + abs(frontier[1] - pacman_pos[1])
            distance = len(a_star(graph, pacman_pos, frontier))
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

# Used to find our path to the superfruit
def risk_aware_bfs(graph, pacman_pos, super_fruit_pos, ghost_positions, food_positions):
    """
    Uses Risk-Aware Best-First Search to guide Pac-Man towards the super fruit efficiently,
    while avoiding high-risk ghost areas.
    """
    if not super_fruit_pos:
        return []  # No fruit available

    # Priority queue for best-first search
    open_set = []
    heapq.heappush(open_set, (0, pacman_pos))  # (priority, position)

    came_from = {}  # Stores paths
    cost_so_far = {pacman_pos: 0}  # Stores cost to reach each position

    while open_set:
        _, current = heapq.heappop(open_set)  # Get node with lowest priority

        if current == super_fruit_pos:
            # Reconstruct path
            path = []
            while current != pacman_pos:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in graph.get(current, []):
            # Calculate risk-aware heuristic
            distance_to_fruit = len(a_star(graph, neighbor, super_fruit_pos))
            ghost_penalty = sum(max(0, 5 - len(a_star(graph, neighbor, ghost))) for ghost in ghost_positions)
            food_bonus = -2 if neighbor in food_positions else 0  # Prioritize paths that include food
            
            priority = distance_to_fruit + ghost_penalty + food_bonus  # Total weighted cost

            if neighbor not in cost_so_far or priority < cost_so_far[neighbor]:
                cost_so_far[neighbor] = priority
                came_from[neighbor] = current
                heapq.heappush(open_set, (priority, neighbor))

    return []  # No valid path found


def get_best_food_path(graph, pacman_pos, food_positions):
    """
    Finds the best path to food using MST-based density rather than just distance.
    - Evaluates multiple anchor points and selects the best cluster.
    """
    anchor_points = [
        pacman_pos,  
        (1, len(game_map[1])-2),   # Top Right
        (1, 1),     # Top Left
        (len(game_map)-2, len(game_map[1])-2),    # Bottom Right
        (len(game_map)-2, 1)     # Bottom Left
        (len(game_map) // 2, len(game_map)[len(game_map) // 2] // 2) # Centre 
    ]

    best_path = None
    best_score = -1  # Invalid score

    for anchor in anchor_points:
        total_cost, food_count = compute_partial_mst(graph, anchor, food_positions)
        if food_count == 0:
            continue  # Skip empty clusters

        # Compute a density score: More food, lower cost = better
        density_score = food_count / (total_cost + 1)  # Avoid division by zero

        if density_score > best_score:
            best_score = density_score
            best_path = a_star(graph, pacman_pos, anchor)  # Move toward the best cluster

    return best_path
