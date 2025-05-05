# ai/dqn/model.py

import torch
import torch.nn as nn

class DQNCNN(nn.Module):
    """
    A small CNN with a shared backbone and two heads:
      - collect head: learns Q-values for pellet-gathering
      - escape head: learns Q-values for ghost-avoidance
    
    Input shape: (batch, in_channels, H=15, W=15)
    Output: two tensors of shape (batch, n_actions)
    """
    def __init__(self, in_channels: int = 6, n_actions: int = 4):
        super().__init__()
        # --- Shared convolutional backbone ---
        # 3 × (Conv3x3 → ReLU), padding=1 keeps spatial dim 15×15
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )
        # Flatten 64×15×15 → 14400
        self.flatten = nn.Flatten()
        # Shared bottleneck
        self.fc_shared = nn.Sequential(
            nn.Linear(64 * 15 * 15, 512),
            nn.ReLU(inplace=True),
        )
        # Two separate heads (each → n_actions Q-values)
        self.head_collect = nn.Linear(512, n_actions)
        self.head_escape  = nn.Linear(512, n_actions)

    def forward(self, x: torch.Tensor):
        """
        x: (batch, in_channels, 15, 15)
        returns: (q_collect, q_escape), each (batch, n_actions)
        """
        z = self.conv(x)              # → (batch, 64,15,15)
        z = self.flatten(z)           # → (batch, 64*15*15)
        h = self.fc_shared(z)         # → (batch, 512)
        return self.head_collect(h), self.head_escape(h)
