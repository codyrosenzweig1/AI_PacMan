# replay.py

import pygame
import pickle
import sys
from game.rendering import draw_game
from maps.level1 import game_map

FPS = 10

# 1) Prompt user
choice = None
while choice not in ("best", "worst"):
    choice = input("Replay which trajectory? (best/worst): ").strip().lower()

traj_file = f"data/{choice}_traj.pkl"

# 2) Load trajectory
try:
    with open(traj_file, "rb") as f:
        trajectory = pickle.load(f)
except FileNotFoundError:
    print(f"ERROR: '{traj_file}' not found. Run train.py to generate it.")
    sys.exit(1)

# 3) Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

# 4) Replay loop
for snap in trajectory:
    # allow quitting mid‐replay
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    # Unpack snapshot (we stored snapshots as dicts)
    pacman_pos   = snap["pacman_pos"]
    ghosts       = snap["ghosts"]
    food         = snap["food"]
    fruit        = snap["fruit"]
    ghost_hunter = snap["ghost_hunter"]

    # Draw the current frame
    draw_game(
        screen,
        game_map,
        pacman_pos,
        ghosts,
        food,
        fruit,
        ghost_hunter
    )

    pygame.display.flip()
    clock.tick(FPS)

# 5) Pause on last frame then exit
pygame.time.wait(1000)
pygame.quit()
