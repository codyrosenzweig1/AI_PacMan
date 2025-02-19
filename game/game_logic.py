import random
from ai.search import smarter_a_star
from ai.path_manager import get_exploration_path
from game.settings import PATH_INDEX

path_index = 0

def move_ghosts(graph, ghosts):
    """
    Moves ghosts randomly each turn. Ghosts stay within valid paths.
    """
    return [random.choice(graph[ghost]) if ghost in graph else ghost for ghost in ghosts]

visited = set()  # Keeps track of explored tiles

def update_game(graph, pacman_pos, ghost_positions, food_positions, super_fruit_pos):
    """
    Updates Pac-Man’s movement while tracking explored tiles and avoiding ghosts.
    """
    global visited

    # Mark Pac-Man’s current position as visited
    visited.add(pacman_pos)
    
    # Remove food is Pac-Man steps on food tile
    if pacman_pos in food_positions:
        food_positions.remove(pacman_pos) # PacMan eats the food
        # update his score
        
    # Remove super_fruit if Pac-Man steps on food tile
    if pacman_pos in super_fruit_pos:
        super_fruit_pos.remove(pacman_pos) # PacMan eats the food
        # update his score
        # Change his state

    # Get a new path if needed
    path = get_exploration_path(graph, pacman_pos, visited, ghost_positions, super_fruit_pos)

    print(path)

    # Move Pac-Man along the path
    if path:
        pacman_pos = path.pop(1)
        print("Pacman pos:", pacman_pos)
        print("path:,", path)

    # Move ghosts
    ghost_positions = move_ghosts(graph, ghost_positions)

    return pacman_pos, ghost_positions, food_positions, super_fruit_pos