# ai/dqn/utils.py

import os
import torch
import torch.nn.functional as F

def get_device():
    """
    Return the best available device: MPS (Mac), else CPU.
    """
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

def sync_target_network(source: torch.nn.Module,
                        target: torch.nn.Module):
    """
    Hard update: copy source network weights into target.
    Call every N steps or episodes.
    """
    target.load_state_dict(source.state_dict())

def huber_loss(predictions, targets, delta: float = 1.0):
    """
    Smooth L1 / Huber loss, robust to outliers.
    Equivalent to PyTorch's nn.SmoothL1Loss(reduction='none') with beta=delta.
    """
    return F.smooth_l1_loss(predictions, targets, beta=delta)
