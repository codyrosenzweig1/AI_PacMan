from collections import deque
from heapq import heappop, heappush  # Min-heap for priority queue


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
    """ Manhattan Distance heuristic function for A* """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_food_density(graph, position, food_positions):
    """ 
    Returns a score based on how many food pellets are in a nearby area.
    The more food around, the lower the cost (higher incentive).
    """
    food_count = sum(1 for neighbor in graph[position] if neighbor in food_positions)
    return -10 * food_count  # Negative cost encourages food-rich areas

def get_penalty(position, visited_count, ghost_positions):
    """
    Computes the penalty for a given position based on:
    - Ghost proximity (high penalty)
    - Revisiting tiles (small penalty)
    """
    penalty = 0

    # Ghost danger penalty
    for ghost in ghost_positions:
        if heuristic(position, ghost) <= 2:  # If ghost is 2 tiles away or less
            penalty += 50  # Heavy penalty for danger zones

    # Revisiting tiles penalty
    penalty += 5 * visited_count.get(position, 0)  # Small penalty for repeated visits

    return penalty

def smarter_a_star(graph, start, food_positions, ghost_positions):
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
    heappush(open_list, (0, start, []))  # (f(n), current_position, path_so_far)
    visited_count = {}  # Tracks how many times a tile is visited

    while open_list:
        f_score, current, path = heappop(open_list)

        if current in food_positions:  # Stop at first food location
            return path + [current]

        # Track visits to discourage excessive backtracking
        visited_count[current] = visited_count.get(current, 0) + 1

        for neighbor in graph[current]:  # Explore all neighbors
            g_score = len(path) + 1
            h_score = min(heuristic(neighbor, food) for food in food_positions)  # Closest food cluster
            p_score = get_penalty(neighbor, visited_count, ghost_positions) + get_food_density(graph, neighbor, food_positions)
            f_score = g_score + h_score + p_score

            heappush(open_list, (f_score, neighbor, path + [current]))

    return []  # Return empty path if no valid path found

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





def bfs(maze, start, goal):
    """
    Performs bfs to find the shortest path
    
    Returns a list of (row, col) positions representing the shortest path
    """
    rows, cols = len(maze), len(maze[0]) # Dimensions of the maze
    queue = deque([(start, [])]) # Current position, path_so_far
    visited = set()
    bfs_exploration = []
    
    while queue:
        (current, path) = queue.popleft() # get the front element
        
        bfs_exploration.append(current)
        
        # If we reach the goal, return the path
        if current == goal:
            return path + [current], bfs_exploration # Include final position
        
        # Mark as visited
        visited.add(current)
        
        # Possible moves (Up, down, left , right)
        moves = [
            (0, 1), # Right
            (0, -1), # Left
            (1, 0), # Down
            (-1, 0) # Up
        ]
        
        for move in moves:
            new_row, new_col = current[0] + move[0], current[1] + move[1]
            new_pos = (new_row, new_col)
            
            # Check if new position is valid (inside the maze, not a wall)
            if (0 <= new_row < rows and 0 <= new_col < cols and
                maze[new_row][new_col] != "#" and new_pos not in visited):
                
                queue.append((new_pos, path + [current])) # Add new position -> current position and path to get there
                
    return [], bfs_exploration