import heapq
from collections import deque
from heapq import heappop, heappush  # Min-heap for priority queue
from ai.lookup_table import load_lookup_table

lookup_table = load_lookup_table()  # Load precomputed distances

def build_graph(maze):
    """
    Converts a grid-based maze into an adjacency list graph.

    Parameters:
    - maze: List of strings representing the maze layout.

    Returns:
    - graph: Dictionary where keys are (row, col) positions and values are lists of adjacent positions.
    - start: The starting position of Pac-Man.
    - goal: The position of the power-up fruit.
    """
    graph = {}
    start, goal = None, None
    rows, cols = len(maze), len(maze[0])

    # Define possible movement directions (Up, Down, Left, Right)
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for row in range(rows):
        for col in range(cols):
            if maze[row][col] == "#":
                continue  # Skip walls

            # Identify Pac-Man and the fruit
            if maze[row][col] == "P":
                start = (row, col)
            elif maze[row][col] == "F":
                goal = (row, col)

            # Create an entry in the graph
            graph[(row, col)] = []

            # Check possible moves
            for move in moves:
                new_row, new_col = row + move[0], col + move[1]
                if 0 <= new_row < rows and 0 <= new_col < cols and maze[new_row][new_col] != "#":
                    graph[(row, col)].append((new_row, new_col))  # Connect the nodes

    return graph, start, goal


# Smarter A * search which includes considerations about food density, ghost proximity

def heuristic(a, b):
    # If the distance is precomputed, use it; otherwise fallback to Manhattan
    if lookup_table and a in lookup_table and b in lookup_table[a]:
        return lookup_table[a][b]
    else:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_threat_clear(tile, ghost, game_map):
    """
    Check if there is a clear path between a tile and a ghost.
    If a wall '#' or a super fruit 'F' is between them, the ghost is not a threat
    """
    row_diff, col_diff = ghost[0] - tile[0], ghost[1] - tile[1]
    
    # If ghost is in the same row
    if row_diff == 0:
        step = 1 if col_diff > 0 else -1
        for col in range(tile[1] + step, ghost[1], step):
            if game_map[tile[0]][col] in ('#', 'F'):  # Wall or super fruit blocks the threat
                return False
            
    # If ghost is in the same column
    if col_diff == 0:
        step = 1 if row_diff > 0 else -1
        for row in range(tile[0] + step, ghost[0], step):
            if game_map[row][tile[1]] in ('#', 'F'):  # Wall or super fruit blocks the threat
                return False
            
    return True  # No blocking obstacles, ghost is a real threat

def get_food_density(graph, position, food_positions):
    """ 
    Returns a score based on how many food pellets are in a nearby area.
    The more food around, the lower the cost (higher incentive).
    """
    food_count = sum(1 for neighbor in graph[position] if neighbor in food_positions)
    return -10 * food_count  # Negative cost encourages food-rich areas

def compute_ghost_penalty(tile, ghost_positions, game_map, radius=5):
    """
    Calculates the penalty for a given tile based on its distance to ghosts.
    If a wall or super fruit blocks the ghost, no penalty is applied.
    """
    penalty = 0  # Default penalty (no ghost nearby)
    
    for ghost in ghost_positions:
        distance = heuristic(tile, ghost)  # Compute Manhattan distance to ghost
        
        # If there's no clear threat, skip the penalty
        if not is_threat_clear(tile, ghost, game_map):
            continue  # Ignore this ghost if it's blocked

        if distance == 0:
            penalty += 100  # Tile directly occupied by ghost (very high penalty)
        elif distance == 1:
            penalty += 50   # Immediate neighbor of ghost (high risk)
        elif distance == 2:
            penalty += 20   # Near ghost (medium risk)
        elif distance == 3:
            penalty += 10   # Further from ghost (low risk)
        # Beyond distance 3, no penalty applied
        
    return penalty

def smarter_a_star(graph, start, goal, ghost_positions, game_map):
    """
    Smarter A* Search Algorithm for Pac-Man that considers:
    - Food clusters (higher reward)
    - Ghost avoidance (danger penalty)
    - Revisiting penalties (soft discouragement)

    Parameters:
    - graph: Adjacency list of the maze
    - start: Pac-Man's starting position
    - food_positions: Set of food pellet locations
    - ghost_positions: Set of ghost positions

    Returns:
    - A list of (row, col) positions representing the best path
    """
    open_list = []
    heappush(open_list, (0, start, []))  # (f_score, current_tile, path)
    visited = set()

    while open_list:
        f_score, current, path = heappop(open_list)  # Get tile with lowest f_score

        if current in goal:
            return path + [current]  # If we reached a frontier, return the path

        visited.add(current)

        for neighbor in graph[current]:  # Check all adjacent tiles
            if neighbor not in visited:
                ghost_penalty = compute_ghost_penalty(neighbor, ghost_positions, game_map)  # Dynamic ghost danger
                g_score = len(path) + 1 + ghost_penalty  # Path cost
                h_score = heuristic(neighbor, list(goal)[0])  # Estimated remaining cost
                heappush(open_list, (g_score + h_score, neighbor, path + [current]))

    return []  # No path found

def compute_partial_mst(graph, start_pos, food_positions):
    """
    Computes a partial Minimum Spanning Tree (MST) from a given position.
    - Uses Prim's algorithm to connect food clusters.
    - Returns the total MST cost and number of food items in the MST.
    """
    if not food_positions:
        return 0, 0  # No food, no density

    visited = set()
    min_heap = [(0, start_pos)]  # (cost, position)
    total_cost = 0
    food_count = 0

    while min_heap:
        cost, node = heapq.heappop(min_heap)

        if node in visited:
            continue
        visited.add(node)

        # Count only food nodes
        if node in food_positions:
            food_count += 1
            total_cost += cost  # Add the cost of reaching this food

        # Expand neighbors
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(min_heap, (len(a_star(graph, node, neighbor)), neighbor))

    return total_cost, food_count

def a_star(graph, start, goal):
    """
    A* Search Algorithm for shortest pathfinding using a graph.

    Parameters:
    - graph: Dictionary of nodes and their connections.
    - start: Tuple (row, col) for Pac-Man's position.
    - goal: Tuple (row, col) for the target position.

    Returns:
    - A list of (row, col) positions representing the shortest path.
    """
    open_list = []
    heappush(open_list, (0, start, []))  # (f(n), current_position, path_so_far)
    visited = set()

    while open_list:
        f_score, current, path = heappop(open_list)

        if current == goal:
            return path + [current]  # Return full path

        visited.add(current)

        for neighbor in graph[current]:  # Iterate over directly connected nodes
            if neighbor not in visited:
                g_score = len(path) + 1
                h_score = heuristic(neighbor, goal)
                f_score = g_score + h_score

                heappush(open_list, (f_score, neighbor, path + [current]))

    return []  # Return empty path if no valid path found