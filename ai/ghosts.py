# ai/ghosts.py

import random
from maps.level1 import game_map
from ai.search     import a_star

# ─── FRAME COUNTERS ───────────────────────────────────────────────────────────
# Now these are in *frames*, not seconds
SCATTER_FRAMES = 60   # e.g. 60 frames (~1 second at 60 FPS, or 20 FPS → 3s)
CHASE_FRAMES   = 120  # how many frames you chase
WANDER_FRAMES  = 30   # how many frames you wander at a corner

# Predefined scatter targets (corner positions)
SCATTER_TARGETS = {
    "Blinky": (1, len(game_map[1]) - 2),
    "Pinky":  (1, 1),
    "Inky":   (len(game_map) - 2, len(game_map[1]) - 2),
    "Clyde":  (len(game_map) - 2, 1),
}

class Ghost:
    def __init__(self, name, start_pos):
        self.name            = name
        self.start_pos       = start_pos
        self.position        = start_pos
        self.scatter_target  = SCATTER_TARGETS.get(name, start_pos)

        # frame-based mode counter:
        self.mode           = "scatter"
        self.mode_counter   = SCATTER_FRAMES

        # when at target-corner, we'll wander:
        self.wander_counter = 0

    def respawn(self):
        """Put the ghost back in its house in scatter mode."""
        self.position       = self.start_pos
        self.mode           = "scatter"
        self.mode_counter   = SCATTER_FRAMES
        self.wander_counter = 0

    def update_mode(self):
        """Count down the frame counter and switch modes when it hits zero."""
        self.mode_counter -= 1
        if self.mode == "scatter" and self.mode_counter <= 0:
            self.mode         = "chase"
            self.mode_counter = CHASE_FRAMES
        elif self.mode == "chase" and self.mode_counter <= 0:
            self.mode         = "scatter"
            self.mode_counter = SCATTER_FRAMES

    def move_ghost(self, graph, pacman_pos):
        self.update_mode()

        # If we're in wander period, just decrement that:
        if self.wander_counter > 0:
            self.wander_counter -= 1
            moves = graph[self.position]
            if moves:
                self.position = random.choice(moves)
            return

        if self.mode == "scatter":
            # once we reach the corner, start wandering
            if self.position == self.scatter_target:
                self.wander_counter = WANDER_FRAMES
                return
            # otherwise pathfind there
            path = a_star(graph, self.position, self.scatter_target)
        else:  # chase
            path = a_star(graph, self.position, pacman_pos)

        if path and len(path) > 1:
            self.position = path[1]


def update_ghosts(graph, pacman_pos, ghost_hunter):
    """
    Moves each ghost, and if collision+hunter, calls respawn().
    """
    for ghost in ghosts:
        old = ghost.position
        ghost.move_ghost(graph, pacman_pos)

        if ghost.position == pacman_pos and ghost_hunter:
            ghost.respawn()

    return [g.position for g in ghosts]

def reset_ghosts():
    """
    Reset every Ghost instance to its starting corner and scatter mode,
    with all frame-counters cleared.
    """
    for g in ghosts:
        g.respawn()

# Instantiate your ghosts
ghosts = [
    Ghost("Blinky", (1, len(game_map[1]) - 2)),
    # Ghost("Inky",   (len(game_map) - 2, len(game_map[1]) - 2)),
]
