#!/usr/bin/env python3

import pickle
import matplotlib.pyplot as plt

def plot_returns(episodes, scores, window=50):
    """
    Plot per-episode scores and a moving average over 'window' episodes.
    """
    mov_avg = []
    for i in range(len(scores)):
        start = max(0, i - window + 1)
        mov_avg.append(sum(scores[start:i+1]) / (i - start + 1))

    plt.figure(figsize=(10, 6))
    plt.plot(episodes, scores, alpha=0.3, label='Score per episode')
    plt.plot(episodes, mov_avg,   label=f'{window}-episode moving avg', linewidth=2)
    plt.xlabel('Episode')
    plt.ylabel('Score')
    plt.title('Pac-Man Q-Learning Performance')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 1) load returns.pkl
    with open("data/returns.pkl", "rb") as f:
        data = pickle.load(f)  # [(ep, score, steps), ...]

    # 2) unpack into separate lists
    episodes = [ep    for ep, score, steps in data]
    scores   = [score for ep, score, steps in data]

    # 3) call the plot function
    plot_returns(episodes, scores, window=50)
