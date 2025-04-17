import time
import random
from maps.level1 import game_map
from ai.search import a_star  # Import A* for pathfinding

# Mode durations in seconds
SCATTER_DURATION = 4
CHASE_DURATION = 7
WANDER_DURATION = 3

# Predefined scatter targets (corner positions)
SCATTER_TARGETS = {
    "Blinky": (1, len(game_map[1])-2),   # Top Right
    "Pinky": (1, 1),     # Top Left
    "Inky": (len(game_map)-2, len(game_map[1])-2),    # Bottom Right
    "Clyde": (len(game_map)-2, 1)     # Bottom Left
}

class Ghost:
    def __init__(self, name, start_pos):
        """
        Initializes a ghost with scatter and chase behavior.
        """
        self.name = name
        self.start_pos = start_pos
        self.position = start_pos
        self.scatter_target = SCATTER_TARGETS.get(name, (1, 1))
        self.mode = "scatter"  # Start in Scatter Mode
        self.last_switch_time = time.time()  # Track last mode switch
        self.wander_timer = 0  # Tracks how long ghost randomly moves

    def respawn(self):
        self.position = self.start_pos # need to change to ghost area when we update map. 
        self.mode = "scatter"  # Reset to Scatter Mode
        self.last_switch_time = time.time()
        self.wander_timer = 0 # reset wnder timer

    def update_mode(self):
        """
        Switches between Scatter and Chase mode based on real-world time.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_switch_time

        if self.mode == "scatter" and elapsed_time >= SCATTER_DURATION:
            self.mode = "chase"
            self.last_switch_time = current_time  # Reset timer
        elif self.mode == "chase" and elapsed_time >= CHASE_DURATION:
            self.mode = "scatter"
            self.last_switch_time = current_time  # Reset timer
        

    def move_ghost(self, graph, pacman_pos):
        """
        Moves ghosts based on their mode.
        """
        self.update_mode()  # Check if mode should switch

        if self.mode == "scatter":
            # print("Name;", self.name)
            # print("Scatter", self.mode)
            self.scatter_movement(graph)  # Scatter Mode Behavior
        else:
            # print("Name;", self.name)
            # print("Chase;", self.mode)
            self.chase_movement(graph, pacman_pos)  # Chase Mode Behavior

    def scatter_movement(self, graph):
        """
        Controls ghost movement in Scatter Mode.
        """
        if self.wander_timer > 0:  
            # Randomly wander for a few moves
            self.wander_timer -= 1  
            possible_moves = graph[self.position]
            # print(graph)
            if possible_moves:
                self.position = random.choice(possible_moves)
            return

        # If ghost reaches scatter target, start wandering
        if self.position == self.scatter_target:
            self.wander_timer = WANDER_DURATION * 5  # Convert seconds to frames (assuming 30 FPS)
            return

        # Move towards scatter target using A*
        path = a_star(graph, self.position, self.scatter_target)
        if path and len(path) > 1:
            self.position = path[1]  # Move to next step in the path

    def chase_movement(self, graph, pacman_pos):
        """
        Controls ghost movement in Chase Mode (A* search towards Pac-Man).
        """
        path = a_star(graph, self.position, pacman_pos)
        if path and len(path) > 1:
            self.position = path[1]  # Move towards Pac-Man

def update_ghosts(graph, pacman_pos, ghost_hunter):
    """
    Updates all ghosts' movements based on their current mode.
    """
    for ghost in ghosts:
        ghost.move_ghost(graph, pacman_pos)

        if ghost.position == pacman_pos:
            if ghost_hunter:
                ghost.respawn()



    return [ghost.position for ghost in ghosts]  # Return updated ghost positions

# Create ghost instances with names and starting positions
# Tracks their current positions
ghosts = [
    Ghost("Blinky", (1, len(game_map[1])-2)),   # Top Right),
    #Ghost("Pinky", (1, 1)), # Top Left
    Ghost("Inky", (len(game_map)-2, len(game_map[1])-2)), #bottom Right
    #Ghost("Clyde",  (len(game_map)-2, 1)) # Bottom LEft
]