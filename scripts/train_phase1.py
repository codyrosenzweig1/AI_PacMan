# train_phase1.py

import pickle
from maps.level1       import game_map as _orig_map
from ai.path_manager   import get_initial_path
from game.score_tracker import reset_score
from ai.rl_utils       import make_state, choose_action, update_q
from ai.env            import step_environment
from ai.lookup_table   import load_lookup_table
from ai.ghosts         import reset_ghosts
import statistics

# Hyperparams (tweak or use your BO results)
ALPHA        = 0.1
GAMMA        = 0.9
EPS_DECAY    = 0.9995
MIN_EPS      = 0.1
NUM_EPISODES = 10000
MAX_STEPS    = 1000

# 1) Build a "no-fruit" map
nofruit_map = [ row.replace('F','.') for row in _orig_map ]

# 2) Prepare Q and lookup table
Q      = {}
lookup = load_lookup_table()

# 3) Training
episode_returns = []
epsilon = 1.0

for ep in range(NUM_EPISODES):
    reset_score()
    reset_ghosts()
    # reset ghosts into house if needed
    path, pacman_pos, ghosts, food, fruit, graph = get_initial_path(nofruit_map)
    fruit        = None
    ghost_hunter = False
    hunter_timer = 0
    done         = False
    steps        = 0

    # initial state
    state = make_state(pacman_pos, ghosts, food, fruit, ghost_hunter, lookup)

    while not done and steps < MAX_STEPS:
        # a) choose an action
        action = choose_action(pacman_pos, state, graph, Q, epsilon)

        # b) step the env and get back a reward
        (pacman_pos,
         ghosts,
         food,
         fruit,
         ghost_hunter,
         hunter_timer,
         done,
         reward) = step_environment(
            graph,
            action,
            ghosts,
            food,
            fruit,
            ghost_hunter,
            hunter_timer
        )

        # c) update Q-table
        next_state = make_state(pacman_pos, ghosts, food, fruit, ghost_hunter, lookup)
        update_q(Q, state, action, reward, next_state, ALPHA, GAMMA)
        state = next_state

        steps += 1

    episode_returns.append(reward)      # last-step reward or simply get_score()
    epsilon = max(MIN_EPS, epsilon * EPS_DECAY)
    print(f"Phase1 Ep {ep:4d} | Steps {steps:4d} | ε={epsilon:.3f}")

# 4) Save bootstrapped Q
with open("data/q_table_phase1.pkl","wb") as f:
    pickle.dump(Q, f)
