import pickle
from maps.level1 import game_map
from ai.path_manager import get_initial_path
from game.score_tracker import reset_score, get_score
from ai.rl_utils import make_state, choose_action, update_q
from ai.env import step_environment
from ai.lookup_table import load_lookup_table
from ai.ghosts import reset_ghosts

# Hyperparameters
NUM_EPISODES = 5000
MAX_STEPS    = 1000
ALPHA        = 0.0995     # learning rate
GAMMA        = 0.8684      # discount factor
EPSILON      = 1.0      # initial exploration
EPS_DECAY    = 0.9995    # decay per episode
MIN_EPSILON  = 0.1

episode_returns = []

# Q and lookup distance table
Q = {}
lookup_table = load_lookup_table()

# tracking best and worst games
best_score  = float("-inf")
worst_score = float("inf")
best_traj   = None
worst_traj  = None

for ep in range(NUM_EPISODES):
    # 1) Reset everything
    reset_score()
    reset_ghosts()
    path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph = \
        get_initial_path(game_map)
    ghost_hunter = False
    hunter_timer = 0
    step_count = 0
    prev_score = 0

    state = make_state(
        pacman_pos,
        ghost_positions,
        food_positions,
        super_fruit_pos,
        ghost_hunter,
        lookup_table
    )

    # Trajectory for this episode
    current_traj = []

    # 2) Inner loop
    done = False
    while step_count < MAX_STEPS and not done:
        # 2a) Choose & execute action
        action = choose_action(pacman_pos, state, graph, Q, EPSILON)


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

        # Record a snapshot
        current_traj.append({
            "pacman_pos":   pacman_pos,
            "ghosts":       ghost_positions.copy(),
            "food":         food_positions.copy(),
            "fruit":        super_fruit_pos,
            "ghost_hunter": ghost_hunter
        })

        # 2b) Observe reward
        curr_score = get_score()
        reward = curr_score - prev_score
        prev_score = curr_score

        # 2c) New state & Q‑update
        next_state = make_state(
            pacman_pos, ghost_positions, food_positions,
            super_fruit_pos, ghost_hunter, lookup_table
        )
        update_q(Q, state, action, reward, next_state, ALPHA, GAMMA)
        state = next_state

        step_count += 1

    # End of episode: compare scores
    total = get_score()
    if total > best_score:
        best_score = total
        best_traj  = current_traj.copy()
    if total < worst_score:
        worst_score = total
        worst_traj  = current_traj.copy()

    # 3) End of episode
    episode_returns.append((total, done, step_count))
    print(f"Episode {ep:3d} | Score {int(total):4d} | Steps {step_count} | ε={EPSILON:.3f}")

    # Decay ε
    EPSILON = max(MIN_EPSILON, EPSILON * EPS_DECAY)

# 4) Save Q‑table for demo.py
with open("data/worst_traj.pkl", "wb") as f: 
    pickle.dump(worst_traj, f)

with open("data/best_traj.pkl", "wb") as f: 
    pickle.dump(best_traj, f)

with open("data/q_table.pkl","wb") as f:
    pickle.dump(Q, f)

with open("data/returns.pkl", "wb") as f:
    pickle.dump([r[0] for r in episode_returns], f)    


