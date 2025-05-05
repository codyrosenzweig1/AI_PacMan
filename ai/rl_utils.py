# ai/rl_utils.py

import random

def make_state(pacman_pos,
               ghost_positions,
               food_positions,
               super_fruit_pos,
               power_mode,
               lookup_table):
    """
    Build a hashable state tuple:
      (dot_bin, fruit_bin, ghost_bin,
       dot_dir, fruit_dir, ghost_dir,
       pm_flag)
    """

    pr, pc = pacman_pos

    # 1) Nearest dot
    if food_positions:
        dot_dists = {
            f: lookup_table[pacman_pos].get(f, float('inf'))
            for f in food_positions
        }
        target_dot, d_dot = min(dot_dists.items(), key=lambda x: x[1])
    else:
        target_dot, d_dot = pacman_pos, 0

    # 2) Super-fruit distance
    if super_fruit_pos is not None:
        d_fruit = lookup_table[pacman_pos].get(super_fruit_pos, float('inf'))
        target_fruit = super_fruit_pos
    else:
        d_fruit = float('inf')
        target_fruit = pacman_pos

    # 3) Nearest ghost
    if ghost_positions:
        ghost_dists = [
            lookup_table[pacman_pos].get(g, float('inf'))
            for g in ghost_positions
        ]
        d_ghost = min(ghost_dists)
        idx = ghost_dists.index(d_ghost)
        target_ghost = ghost_positions[idx]
    else:
        d_ghost = float('inf')
        target_ghost = pacman_pos

    # 4) Bucket distances
    def bucket(d):
        if d == 0:    return 0
        if d <= 3:    return 1
        if d <= 7:    return 2
        return 3

    dot_bin   = bucket(d_dot)
    fruit_bin = bucket(d_fruit)
    ghost_bin = bucket(d_ghost)

    # 5) Direction helpers (0=N,1=E,2=S,3=W)
    def direction_to(target):
        tr, tc = target
        dr, dc = tr - pr, tc - pc
        if dr == 0 and dc == 0:
            return 0
        if abs(dr) > abs(dc):
            return 0 if dr < 0 else 2
        return 1 if dc > 0 else 3

    dot_dir   = direction_to(target_dot)
    fruit_dir = direction_to(target_fruit)
    ghost_dir = direction_to(target_ghost)

    # 6) Power-mode flag
    pm_flag = 1 if power_mode else 0

    return (
        dot_bin,
        fruit_bin,
        ghost_bin,
        dot_dir,
        fruit_dir,
        ghost_dir,
        pm_flag
    )


def choose_action(pacman_pos, state, graph, Q, epsilon):
    """
    Epsilon-greedy over the valid neighbor moves.
    - pacman_pos: current (r,c)
    - state: the tuple from make_state
    - graph: adjacency dict of valid moves
    - Q: { state: { action: value } }
    - epsilon: probability of random action
    """
    valid = graph[pacman_pos]

    # explore
    if random.random() < epsilon:
        return random.choice(valid)

    # exploit: ensure Q[state] exists
    q_s = Q.setdefault(state, {})
    # ensure each valid action has an entry
    for a in valid:
        q_s.setdefault(a, 0.0)

    # pick the neighbor with max Q-value
    return max(valid, key=lambda a: q_s[a])


def update_q(Q, state, action, reward, next_state, alpha, gamma):
    """
    Tabular Q-learning:
      Q[s][a] += alpha * (reward
                          + gamma * max_a' Q[s'][a']
                          - Q[s][a])
    """
    # ensure dicts exist
    Q.setdefault(state, {})
    Q[state].setdefault(action, 0.0)
    Q.setdefault(next_state, {})

    # find best next-value
    future_vals = Q[next_state].values()
    best_next = max(future_vals, default=0.0)

    # TD-error update
    old = Q[state][action]
    Q[state][action] = old + alpha * (reward + gamma * best_next - old)
