# ai/dqn/replay_buffer.py

import random
from collections import deque
import torch

class ReplayBuffer:
    """
    A fixed-size ring buffer of transitions for experience replay.
    Stores tuples: (state, action, reward, next_state, done)
    All elements are PyTorch tensors or primitives.
    """
    def __init__(self, capacity: int = 50000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """Add one transition to the buffer."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        """
        Randomly sample a batch of transitions.
        Returns five tensors, each with leading dim = batch_size.
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.stack(states),
            torch.tensor(actions, dtype=torch.int64),
            torch.tensor(rewards, dtype=torch.float32),
            torch.stack(next_states),
            torch.tensor(dones, dtype=torch.float32),
        )

    def __len__(self):
        return len(self.buffer)
