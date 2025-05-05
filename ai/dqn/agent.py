# ai/dqn/agent.py

import random
import torch
import torch.optim as optim
import numpy as np

from ai.dqn.model import DQNCNN
from ai.dqn.replay_buffer import ReplayBuffer
from ai.dqn.utils import get_device, sync_target_network, huber_loss

class DQNAgent:
    """
    Encapsulates online & target networks, replay buffer, optimizer,
    epsilon scheduling, and the core DQN update logic.
    """
    def __init__(self,
                 in_channels: int = 6,
                 n_actions: int = 4,
                 lr: float = 1e-4,
                 gamma: float = 0.99,
                 batch_size: int = 32,
                 buffer_size: int = 50_000,
                 target_update_freq: int = 1_000,
                 seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.device = get_device()
        # Networks
        self.online = DQNCNN(in_channels, n_actions).to(self.device)
        self.target = DQNCNN(in_channels, n_actions).to(self.device)
        sync_target_network(self.online, self.target)

        # Optimiser
        self.optimizer = optim.Adam(self.online.parameters(), lr=lr)

        # Replay buffer
        self.buffer = ReplayBuffer(capacity=buffer_size)

        # Hyperparams
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.steps_done = 0
        self.epsilon = 1.0  # will be decayed externally

    def select_action(self,
                      q_collect: torch.Tensor,
                      q_escape:  torch.Tensor,
                      valid_mask: torch.Tensor,
                      power_mode: bool,
                      threat: bool) -> int:
        """
        Epsilon-greedy over the chosen head (escape if in threat & not powered).
        valid_mask: 1×n_actions boolean mask of legal moves.
        """
        # Choose which head to use
        if threat and not power_mode:
            q = q_escape
        else:
            q = q_collect

        # Mask invalid moves
        invalid = (~valid_mask).to(self.device)
        q = q.masked_fill(invalid, -1e9)

        # Epsilon-greedy
        if random.random() < self.epsilon:
            valid_indices = valid_mask.nonzero(as_tuple=False).view(-1).tolist()
            return random.choice(valid_indices)
        else:
            return int(q.argmax(dim=1).item())

    def optimise_model(self):
        """
        Sample a batch, compute DQN loss with Huber, backpropagate,
        and occasionally sync the target net.
        """
        if len(self.buffer) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones = \
            self.buffer.sample(self.batch_size)
        states      = states.to(self.device)
        actions     = actions.to(self.device)
        rewards     = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones       = dones.to(self.device)

        # Compute current Q-values
        q_col, q_esc = self.online(states)
        # We only used the chosen head's Q for the action taken
        q_pred = torch.where(dones.unsqueeze(1)==1,
                             torch.zeros_like(q_col),
                             q_col).gather(1, actions.unsqueeze(1)).squeeze(1)
        # Next-state max Q from target net (we pick max over collect head)
        with torch.no_grad():
            next_q_col, next_q_esc = self.target(next_states)
            # We take max over next_q_col if not in threat, but for simplicity we use collect head
            q_next = next_q_col.max(1)[0]
            target = rewards + self.gamma * (1.0 - dones) * q_next

        # Huber loss
        loss = huber_loss(q_pred, target)

        self.optimizer.zero_grad()
        loss.backward()
        # (Optional) gradient clipping:
        torch.nn.utils.clip_grad_norm_(self.online.parameters(), 1.0)
        self.optimizer.step()

        # Update target network?
        self.steps_done += 1
        if self.steps_done % self.target_update_freq == 0:
            sync_target_network(self.online, self.target)

        return loss.item()
