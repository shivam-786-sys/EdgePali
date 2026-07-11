"""
Vectorized spatial similarity + entropy-aware pruning.
No Python loops — pure tensor ops for sub-millisecond execution.
"""

import torch
from core.config import SIMILARITY_THRESHOLD, VARIANCE_SAFETY_THRESHOLD


def compute_similarity_matrix(patches: torch.Tensor) -> torch.Tensor:
    """
    patches: [batch, num_patches, dim]
    returns: [batch, num_patches, num_patches] cosine similarity matrix
    """
    normed = torch.nn.functional.normalize(patches, p=2, dim=-1)
    sim = torch.bmm(normed, normed.transpose(1, 2))
    return sim


def compute_local_variance(patches: torch.Tensor) -> torch.Tensor:
    """
    patches: [batch, num_patches, dim]
    returns: [batch, num_patches] variance per patch (proxy for info entropy)
    """
    return patches.var(dim=-1)


def prune_patches(patches: torch.Tensor):
    """
    Prunes redundant patches based on similarity + variance safety threshold.
    Returns: (pruned_patches_list, keep_mask)
      pruned_patches_list: list of [kept_patches, dim] tensors (variable length per batch)
      keep_mask: [batch, num_patches] bool tensor
    """
    batch_size, num_patches, _ = patches.shape

    sim_matrix = compute_similarity_matrix(patches)          # [B, N, N]
    variance = compute_local_variance(patches)                # [B, N]

    # mask out self-similarity
    eye = torch.eye(num_patches, device=patches.device).bool().unsqueeze(0)
    sim_matrix = sim_matrix.masked_fill(eye, 0.0)

    # a patch is "redundant" if it has a highly similar neighbor
    max_sim, _ = sim_matrix.max(dim=-1)                        # [B, N]
    is_redundant = max_sim > SIMILARITY_THRESHOLD

    # safety net: never prune high-variance (high info) patches
    is_low_info = variance < (variance.mean(dim=-1, keepdim=True) * 0.9)

    prune_mask = is_redundant & is_low_info                    # [B, N]
    keep_mask = ~prune_mask

    pruned_patches_list = [patches[b, keep_mask[b]] for b in range(batch_size)]

    return pruned_patches_list, keep_mask