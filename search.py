from collections import deque

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