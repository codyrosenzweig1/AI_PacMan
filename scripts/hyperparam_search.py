#!/usr/bin/env python3
# hyperparam_search.py

import random
import statistics
import pickle
import optuna

# Project imports — adjust paths if necessary
from maps.level1             import game_map
from ai.path_manager         import get_initial_path
from game.score_tracker      import reset_score, get_score, STEP_PENALTY
from ai.lookup_table         import load_lookup_table
from ai.rl_utils             import make_state, choose_action, update_q
from ai.env                  import step_environment
import ai.ghosts              as gh_module

# ─── Hyperparameter search settings ──────────────────────────────────────────

N_TRIALS   = 30      # total BO evaluations
EPISODES   = 500     # episodes per trial
WINDOW     = 50      # average last WINDOW returns
MAX_STEPS  = 1000    # cap per-episode steps

# ─── Objective function ──────────────────────────────────────────────────────

def run_training(alpha, gamma, eps_decay, step_penalty):
    """
    Run a short Q-learning run with the given hyperparameters.
    Returns the average return over the final WINDOW episodes.
    """
    # 1) Override global step penalty
    STEP_PENALTY = step_penalty

    # 2) Setup
    returns = []
    epsilon = 1.0
    Q = {}
    lookup = load_lookup_table()

    # 3) Episodes
    for ep in range(EPISODES):
        reset_score()
        # Reset ghosts back to their house
        for ghost in gh_module.ghosts:
            ghost.respawn()

        # Initialize game state
        path, pacman_pos, ghost_positions, food_positions, super_fruit_pos, graph = \
            get_initial_path(game_map)
        ghost_hunter = False
        hunter_timer = 0

        state = make_state(
            pacman_pos,
            ghost_positions,
            food_positions,
            super_fruit_pos,
            ghost_hunter,
            lookup
        )

        done = False
        prev_score = 0
        steps = 0

        # 4) Time-step loop
        while not done and steps < MAX_STEPS:
            # a) ε-greedy action
            action = choose_action(pacman_pos, state, graph, Q, epsilon)

            # b) advance environment
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

            # c) compute reward & update Q
            curr = get_score()
            reward = curr - prev_score
            prev_score = curr

            next_state = make_state(
                pacman_pos,
                ghost_positions,
                food_positions,
                super_fruit_pos,
                ghost_hunter,
                lookup
            )
            update_q(Q, state, action, reward, next_state, alpha, gamma)
            state = next_state

            steps += 1

        # end episode
        returns.append(get_score())
        # decay ε
        epsilon = max(0.1, epsilon * eps_decay)

    # mean of last WINDOW returns
    return statistics.mean(returns[-WINDOW:])


def objective(trial):
    # sample hyperparameters
    alpha       = trial.suggest_float("alpha",        0.01,   0.2)
    gamma       = trial.suggest_float("gamma",        0.85,   0.99)
    eps_decay   = trial.suggest_float("eps_decay",    0.990,  0.9995)
    step_penalty= trial.suggest_float("step_penalty",-0.5,   0.0)

    perf = run_training(alpha, gamma, eps_decay, step_penalty)
    return perf


# ─── Run the study ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS)

    print("\n🏆 Best hyperparameters:")
    for k, v in study.best_params.items():
        print(f"  {k:12s} = {v:.4f}")
    print(f"Best avg return (last {WINDOW} eps): {study.best_value:.2f}")

    # Save full trial data
    df = study.trials_dataframe()
    df.to_csv("data/optuna_trials.csv", index=False)
    with open("data/optuna_study.pkl", "wb") as f:
        pickle.dump(study, f)
