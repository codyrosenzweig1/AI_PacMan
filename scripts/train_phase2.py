#!/usr/bin/env python3
import pickle
import math
from maps.level1        import game_map
from ai.path_manager    import get_initial_path
from ai.ghosts          import reset_ghosts
from game.score_tracker import reset_score, get_score
from ai.rl_utils        import make_state, choose_action, update_q
from ai.env             import step_environment
from ai.lookup_table    import load_lookup_table

import torch

print("MPS available?  ", torch.backends.mps.is_available())  # True if PyTorch→MPS is built/installed


# ─── HYPERPARAMETERS ──────────────────────────────────────────────────────────
ALPHA        = 0.1      # learning rate
GAMMA        = 0.9      # discount factor
EPS_DECAY    = 0.9995    # ε decay per episode
MIN_EPS      = 0.1      # ε floor
NUM_EPISODES = 100      # number of episodes to fine-tune
MAX_STEPS    = 1000     # max steps per episode

# ─── BOOTSTRAP PHASE-1 Q and LOOKUP ────────────────────────────────────────────
with open("data/q_table_phase1.pkl","rb") as f:
    Q = pickle.load(f)

lookup = load_lookup_table()

# ─── TRACKERS FOR REPLAY & VISUALISATION ───────────────────────────────────────
best_score  = -math.inf
worst_score =  math.inf
best_traj   = None
worst_traj  = None
returns     = []  # list of (episode, score, steps)

epsilon = 1.0

for ep in range(NUM_EPISODES):
    # Reset score and ghosts each episode
    reset_score()
    reset_ghosts()

    # Initialize a fresh game
    _, pacman_pos, ghosts, food, fruit, graph = get_initial_path(game_map)
    ghost_hunter = False
    hunter_timer = 0
    done         = False
    steps        = 0

    # Prepare to record this episode’s trajectory
    current_traj = []

    # Initial state
    state = make_state(pacman_pos, ghosts, food, fruit, ghost_hunter, lookup)

    while not done and steps < MAX_STEPS:
        # 1) ε-greedy action
        action = choose_action(pacman_pos, state, graph, Q, epsilon)

        # 2) Step environment – now returns reward too
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

        # 3) Record snapshot for replay
        current_traj.append({
            "pacman_pos":   pacman_pos,
            "ghosts":       ghosts.copy(),
            "food":         food.copy(),
            "fruit":        fruit,
            "ghost_hunter": ghost_hunter
        })

        # 4) Q-learning update
        next_state = make_state(pacman_pos, ghosts, food, fruit, ghost_hunter, lookup)
        update_q(Q, state, action, reward, next_state, ALPHA, GAMMA)
        state = next_state

        steps += 1

    # Episode end: collect final score
    total = get_score()
    returns.append((ep, total, steps))

    # Update best/worst for replay
    if total > best_score:
        best_score = total
        best_traj  = current_traj.copy()
    if total < worst_score:
        worst_score = total
        worst_traj  = current_traj.copy()

    # Decay ε
    epsilon = max(MIN_EPS, epsilon * EPS_DECAY)

    print(f"Phase2 Ep {ep:3d} | Score {total:4d} | Steps {steps:4d} | ε={epsilon:.3f}")

# ─── SAVE EVERYTHING ────────────────────────────────────────────────────────────
with open("data/best_traj.pkl","wb") as f:
    pickle.dump(best_traj, f)

with open("data/worst_traj.pkl","wb") as f:
    pickle.dump(worst_traj, f)

with open("data/q_table_final.pkl","wb") as f:
    pickle.dump(Q, f)

with open("data/returns.pkl","wb") as f:
    pickle.dump(returns, f)

print("Saved: best_traj.pkl, worst_traj.pkl, q_table_final.pkl, returns.pkl")
