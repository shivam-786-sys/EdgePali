"""
Generates dummy multi-vector tensors mimicking ColPali-style output.
Phase 1: no real model — pure shape-accurate mock data.
Phase 2: swap this module's internals with real model inference,
zero changes needed in pruning/quantization layers.
"""

import torch
from core.config import BATCH_SIZE, NUM_PATCHES, EMBEDDING_DIM


def generate_dummy_patch_embeddings(
    batch_size: int = BATCH_SIZE,
    num_patches: int = NUM_PATCHES,
    embedding_dim: int = EMBEDDING_DIM,
    redundancy_ratio: float = 0.4,
) -> torch.Tensor:
    """
    Returns tensor of shape [batch_size, num_patches, embedding_dim].
    Injects artificial redundancy (near-duplicate adjacent patches)
    so pruning logic has realistic patterns to act on.
    """
    base = torch.randn(batch_size, num_patches, embedding_dim)

    num_redundant = int(num_patches * redundancy_ratio)
    for b in range(batch_size):
        idx = torch.randperm(num_patches)[:num_redundant]
        src_idx = torch.randperm(num_patches)[:num_redundant]
        noise = torch.randn(num_redundant, embedding_dim) * 0.01
        base[b, idx] = base[b, src_idx] + noise

    return base