import random
from ai.search import smarter_a_star, a_star
from ai.path_manager import get_exploration_path, escape_path, risk_aware_bfs
from game.settings import PATH_INDEX
from game.score_tracker import update_score, reset_score
from ai.ghosts import Ghost, update_ghosts
from maps.level1 import game_map

visited = set()  # Keeps track of explored tiles
path_index = 0
commitment_counter = 0 # tracks how long pacman commits to an action
current_action = "food" # Default to begin food collection
escape_priority = 0
ghost_hunter = False
hunter_timer = 0 
HUNTER_DURATION = 50

def update_game(graph, pacman_pos, ghost_positions, food_positions, super_fruit_pos):
    """
    Updates Pac-Man’s movement while tracking explored tiles and avoiding ghosts.
    """
    global visited, commitment_counter, current_action, escape_priority
    global ghost_hunter, hunter_timer

    # Mark Pac-Man’s current position as visited
    visited.add(pacman_pos)
    
    # Calculate Priorities
    food_priority, super_fruit_priority, escape_priority = calculate_priorities(
        pacman_pos, ghost_positions, food_positions, super_fruit_pos, escape_priority, graph
    )
    
    # Apply Commitment Factor -> Deafult and priorit list (asc) looking for food -> superfruit -> safety
    if commitment_counter > 0:
        commitment_counter -= 1  # Reduce commitment timer each frame
    else:
        # Determine the highest-priority action
        if escape_priority >= max(food_priority, super_fruit_priority):
            current_action = "escape"
            commitment_counter = 5  # Commit to escaping for at least 5 frames
        elif super_fruit_priority > food_priority:
            current_action = "super_fruit" 
            commitment_counter = 7  # Commit to going for the super fruit longer
        else:
            current_action = "food"
            
    # Decide Pac-Man's Next Move and subsequent next path
    print("Current Action:", current_action)
    if current_action == "escape":
        path = escape_path(graph, pacman_pos, ghost_positions)
    elif current_action == "super_fruit" and super_fruit_pos:
        path = risk_aware_bfs(graph, pacman_pos, super_fruit_pos, ghost_positions, food_positions)
    else:
        path = get_exploration_path(graph, pacman_pos, visited, ghost_positions, food_positions)

    # Move Pac-Man along the path
    if path:
        update_score("step") # update his score for each step
        pacman_pos = path.pop(1)
        if ghost_hunter: # Logic for pacman hunter state managaement
            hunter_timer -= 1
            if hunter_timer <= 0:
                ghost_hunter = False
    
    # Remove food is Pac-Man steps on food tile
    if pacman_pos in food_positions:
        food_positions.remove(pacman_pos) # PacMan eats the food
        update_score("food") # update his score for eating food
        
    # Remove super_fruit if Pac-Man steps on food tile
    if pacman_pos == super_fruit_pos:
        super_fruit_pos = None #.remove(pacman_pos) # PacMan eats the food
        update_score("super_fruit") # update his score for eating super fruit
        ghost_hunter = True # PacMan becomes a ghost hunter
        hunter_timer = HUNTER_DURATION # Set the timer for ghost hunting
        # Change his state

    # Logic for when pacman collides with a ghost
    if pacman_pos in ghost_positions:
        if current_action == "ghost_hunter":
            ghost_positions.remove(pacman_pos)
            update_score("ghost_eaten")
        else:
            update_score("collision") # update his score for colliding with a ghost
            running = False # Pacman Dies 
    
    # Move ghosts
    ghost_positions = update_ghosts(graph, pacman_pos, ghost_hunter)

    return pacman_pos, ghost_positions, food_positions, super_fruit_pos, ghost_hunter

def calculate_priorities(pacman_pos, ghost_positions, food_positions, super_fruit_pos, last_escape_priority, graph):
    """
    Calculates Pac-Man's three main priorities dynamically:
    1. Food priority decreases as food is collected.
    2. Super fruit priority increases as food decreases.
    3. Escape priority is based on ghost proximity and valid paths (avoiding inflation).
    """

    # --- Food Priority ---
    if len(food_positions) > 0:
        food_priority = max(20 - len(food_positions) / 3, 12)  # Minimum priority is 5
    else:
        food_priority = 0  # No food left to collect
    
    # --- Super Fruit Priority ---
    if super_fruit_pos:
        distance_to_fruit = len(a_star(graph, pacman_pos, super_fruit_pos))
        base_fruit_priority = 10 + (30 / (distance_to_fruit + 1))  # Closer = higher priority
        super_fruit_priority = base_fruit_priority + (15 - len(food_positions) / 5)  # Becomes more important later
    else:
        super_fruit_priority = 0  # No super fruit present

    # --- Escape Priority ---
    escape_priority = 10  # Base priority (prevents it from ever being zero)
    total_threat = 0  # Accumulates the total threat from all ghosts

    for ghost in ghost_positions:
        # Distance to ghost using a_star
        distance = len(a_star(graph, pacman_pos, ghost))
        
        # Weighted contribution: closer ghosts contribute more, further ghosts contribute less
        if distance == 1:
            total_threat += 80  # Pac-Man is caught
        elif distance <= 2:
            total_threat += 50 / distance  # High immediate danger
        elif distance <= 4:
            total_threat += 30 / (distance ** 1.5)  # Medium threat with diminishing effect
        elif distance <= 6:
            total_threat += 15 / (distance ** 2)  # Lower danger, further reduced
        else:
            total_threat += 5 / (distance ** 2.5)  # Minimal impact from far ghosts

    # Apply the combined threat level to escape priority
    escape_priority += total_threat
    # Cap escape priority to prevent excessive inflation
    escape_priority = min(100, escape_priority)

    return food_priority, super_fruit_priority, escape_priority
