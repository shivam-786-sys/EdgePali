import torch
import torch.nn as nn
import os

class PatchImportanceScorer(nn.Module):
    def __init__(self, embedding_dim=128, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2), nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1), nn.Sigmoid()
        )
    def forward(self, patches):
        return self.net(patches).squeeze(-1)


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best_scorer.pt")

_scorer = None

def get_scorer():
    global _scorer
    if _scorer is None:
        _scorer = PatchImportanceScorer(embedding_dim=128)
        _scorer.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        _scorer.eval()
    return _scorer


def learned_prune(patches: torch.Tensor, threshold: float = 0.5):
    """
    patches: [num_patches, dim]
    Returns: keep_mask [num_patches] bool
    """
    scorer = get_scorer()
    with torch.no_grad():
        scores = scorer(patches)
    return scores > threshold