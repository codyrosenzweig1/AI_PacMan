import random
from ai.search import smarter_a_star
from game.settings import PATH_INDEX

path_index = 0

# Function to move ghosts around randomly to begin with
def move_ghosts(graph, ghosts):
    new_positions = []
    for ghost in ghosts:
        # print("Graph:", graph)
        # print("ghost:", ghost)
        possible_moves = graph[ghost]  # Get all valid moves for the ghost
        if possible_moves:
            new_positions.append(random.choice(possible_moves))  # Pick a random move
        else:
            new_positions.append(ghost)  # Stay in place if no valid move
    return new_positions

def update_game(graph, path, pacman_pos, ghost_positions):
    """ Update Pac-Man and Ghost movement """
    global path_index
    
    # Pac-Man follows path
    if path and path_index < len(path):
        pacman_pos = path[path_index]
        path_index += 1

    # Move ghosts randomly
    ghost_positions = move_ghosts(graph, ghost_positions)

    return pacman_pos, ghost_positions