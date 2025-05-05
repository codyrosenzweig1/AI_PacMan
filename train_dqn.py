# train_dqn.py

import os
import random
import numpy as np
import torch

from ai.dqn.agent import DQNAgent
from ai.dqn.utils import get_device
from ai.dqn.replay_buffer import ReplayBuffer
from ai.env import step_environment
from ai.path_manager import get_initial_path
from game.score_tracker import reset_score, get_score
from maps.level1 import game_map  # hard-coded for now

# ─── Hyperparameters ────────────────────────────────────────────────
SEED              = 42
NUM_EPISODES      = 500
MAX_STEPS         = 1000
LEVEL_CLEAR_BONUS = 2000     # big reward on clearing all pellets
# (other hyperparams live inside DQNAgent defaults)
# ─────────────────────────────────────────────────────────────────────

# Reproducibility
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = get_device()
print(f"Using device: {device}")

# Create checkpoint folder
CKPT_DIR = "checkpoints"
os.makedirs(CKPT_DIR, exist_ok=True)

# Action mapping: up, down, left, right
ACTIONS = [(-1,  0),  # up
           ( 1,  0),  # down
           ( 0, -1),  # left
           ( 0,  1)]  # right

def build_state_tensor(pacman_pos, ghost_positions, food_positions, super_fruit_pos):
    """
    Build a (6×15×15) tensor of floats in [0,1]:
      0: walls
      1: pellets
      2: super-fruit
      3: ghosts
      4: threat map (Manhattan ≤ 3)
      5: Pac-Man
    """
    C, H, W = 6, len(game_map), len(game_map[0])
    state = np.zeros((C, H, W), dtype=np.float32)

    # 0) walls & open
    for r in range(H):
        for c in range(W):
            if game_map[r][c] == "#":
                state[0, r, c] = 1.0

    # 1) pellets (.)
    for (r, c) in list(food_positions):
        state[1, r, c] = 1.0

    # 2) super-fruit (if present)
    if super_fruit_pos:
        state[2, super_fruit_pos[0], super_fruit_pos[1]] = 1.0

    # 3) ghosts
    for (r, c) in ghost_positions:
        state[3, r, c] = 1.0

    # 4) threat map: Manhattan distance ≤ 3
    for (gr, gc) in ghost_positions:
        for r in range(H):
            for c in range(W):
                if abs(gr - r) + abs(gc - c) <= 3:
                    state[4, r, c] = 1.0

    # 5) Pac-Man
    state[5, pacman_pos[0], pacman_pos[1]] = 1.0

    # To torch tensor
    return torch.from_numpy(state).unsqueeze(0).to(device)  # (1,6,15,15)

def main():
    agent = DQNAgent(seed=SEED)
    all_returns = []

    for ep in range(1, NUM_EPISODES + 1):
        # Reset environment & score
        reset_score()
        path, pacman_pos, ghosts, food, fruit, graph = get_initial_path(game_map)
        ghost_hunter, hunter_timer = False, 0

        state = build_state_tensor(pacman_pos, ghosts, food, fruit)
        total_reward = 0

        for step in range(1, MAX_STEPS + 1):
            # 1) Compute legal‐move mask
            neighbours = set(graph[pacman_pos])
            valid_mask = torch.tensor(
                [ (pacman_pos[0]+dr, pacman_pos[1]+dc) in neighbours
                  for dr,dc in ACTIONS ],
                dtype=torch.bool, device=device
            )

            # 2) Forward pass
            with torch.no_grad():
                q_col, q_esc = agent.online(state)

            # 3) Select action
            threat = (valid_mask.sum() > 0)  # crude: if any threat channel active
            action_idx = agent.select_action(
                q_col, q_esc, valid_mask, ghost_hunter, threat
            )
            dr, dc = ACTIONS[action_idx]
            new_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)

            # 4) Step environment
            (pacman_pos, ghosts, food, fruit,
             ghost_hunter, hunter_timer, done) = step_environment(
                 graph, new_pos, ghosts, food, fruit, ghost_hunter, hunter_timer
             )

            # 5) Compute reward
            curr_score = get_score()
            reward = curr_score - total_reward
            total_reward = curr_score

            # Level clear bonus
            if done and not food:
                reward += LEVEL_CLEAR_BONUS

            # 6) Build next state
            next_state = build_state_tensor(pacman_pos, ghosts, food, fruit)

            # 7) Store & optimise
            agent.buffer.push(state, action_idx, reward, next_state, done)
            loss = agent.optimise_model()

            state = next_state

            if done:
                break

        all_returns.append(total_reward)
        agent.epsilon = max(0.1, agent.epsilon * 0.995)  # decay

        print(f"Episode {ep:3d} | Return {total_reward:5.0f} | Steps {step} | ε {agent.epsilon:.3f}")

        # Checkpoint every 10 episodes
        if ep % 10 == 0:
            fname = os.path.join(CKPT_DIR, f"dqn_ep{ep:03d}_ret{int(total_reward)}.pt")
            torch.save(agent.online.state_dict(), fname)

    # Final save
    torch.save(agent.online.state_dict(), os.path.join(CKPT_DIR, "dqn_final.pt"))

if __name__ == "__main__":
    main()
