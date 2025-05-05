# demo.py
import pygame, pickle
from maps.level1 import game_map
from ai.path_manager import get_initial_path
from game.rendering import draw_game
from game.score_tracker import reset_score, get_score
from game.game_logic import update_game            # for rule‑based fallback
from ai.env import step_environment
from ai.rl_utils import make_state, choose_action
from ai.lookup_table import load_lookup_table
from ai.ghosts import reset_ghosts

# ───── CONFIG ────────────────────────────────────────────────
USE_RL = True           # toggle between RL and rule‑based
MODEL_FILE = "data/q_table.pkl"
FPS = 10

# ───── LOAD MODELS & TABLES ───────────────────────────────────
if USE_RL:
    with open(MODEL_FILE, "rb") as f:
        Q = pickle.load(f)
    epsilon = 0.0        # always exploit
lookup_table = load_lookup_table()

# ───── PYGAME SETUP ───────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((600,600))
clock  = pygame.time.Clock()

# ───── INITIALIZE EPISODE ─────────────────────────────────────
reset_score()
reset_ghosts()
path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph = \
    get_initial_path(game_map)

ghost_hunter = False
hunter_timer = 0

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    if USE_RL:
        # 1) Compute current state & choose action
        state  = make_state(
            pacman_pos,
            ghost_positions,
            food_positions,
            super_fruit_pos,
            ghost_hunter,
            lookup_table
        )
        action = choose_action(state, graph, Q, epsilon)

        # 2) Step environment under that action
        (pacman_pos,
         ghost_positions,
         food_positions,
         super_fruit_pos,
         ghost_hunter,
         hunter_timer,
         done) = step_environment(
             graph,
             action,
             ghost_positions,
             food_positions,
             super_fruit_pos,
             ghost_hunter,
             hunter_timer
         )

        if done:
            print("RL demo finished with score", get_score())
            pygame.time.wait(2000)
            break

    else:
        # Rule‑based fallback: use your existing update_game
        pacman_pos, ghost_positions, food_positions, super_fruit_pos, ghost_hunter = \
            update_game(graph,
                        pacman_pos,
                        ghost_positions,
                        food_positions,
                        super_fruit_pos,
                        True)   # pass running‑flag if your signature needs it
        # Note: if your update_game returns a `running` flag or `done` boolean,
        # you may need to adapt this to match its signature.

    # 3) Render
    draw_game(
        screen,
        game_map,
        pacman_pos,
        ghost_positions,
        food_positions,
        super_fruit_pos,
        ghost_hunter
    )
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
