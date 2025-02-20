import time
from maps.level1 import game_map
from ai.search import a_star  # Import A* for pathfinding

# Mode durations in seconds
SCATTER_DURATION = 4
CHASE_DURATION = 12

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
        Initializes a ghost with a starting position and assigned scatter target.
        """
        self.name = name  # e.g., "Blinky", "Pinky"
        self.position = start_pos  # (row, col)
        self.scatter_target = SCATTER_TARGETS.get(name, (1, 1))  # Default to top-left if not found
        self.mode = "chase"  # Start in Scatter Mode
        self.mode_timer = SCATTER_DURATION  # Timer starts at scatter duration
        self.last_switch_time = time.time()  # Track last mode change

    def update_mode(self):
        """
        Switches between Scatter and Chase modes based on the timer.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_switch_time

        if self.mode == "scatter" and elapsed_time >= SCATTER_DURATION:
            self.mode = "chase"
            self.last_switch_time = current_time
        elif self.mode == "chase" and elapsed_time >= CHASE_DURATION:
            self.mode = "scatter"
            self.last_switch_time = current_time

    def move_ghost(self, graph, pacman_pos):
        """
        Moves the ghost based on its current mode.
        - In Scatter Mode, moves toward its assigned scatter target.
        - In Chase Mode, moves toward Pac-Man using A* search.
        """
        self.update_mode()  # Check if mode should switch

        target = self.scatter_target if self.mode == "scatter" else pacman_pos  # Choose target

        # Compute the path to the target using A*
        path = a_star(graph, self.position, target)

        # Move to the next tile if a valid path exists
        if path and len(path) > 1:
            self.position = path[1]  # Move to next step in the path
