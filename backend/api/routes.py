from services.learned_pruning import learned_prune
from fastapi import APIRouter
from services.dummy_generator import generate_dummy_patch_embeddings
from services.tensor_pruning import prune_patches
from services.quantization import compute_scale_zero_point, quantize_tensor
from core.config import TARGET_FOOTPRINT_REDUCTION, TARGET_LATENCY_MS

import time

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/prune")
def prune_and_quantize():
    start = time.perf_counter()

    patches = generate_dummy_patch_embeddings()
    original_count = patches.shape[1]

    pruned_list, keep_mask = prune_patches(patches)

    results = []
    for i, pruned in enumerate(pruned_list):
        scale, zero_point = compute_scale_zero_point(pruned)
        quantized = quantize_tensor(pruned, scale, zero_point)
        results.append({
            "batch_index": i,
            "original_patches": original_count,
            "pruned_patches": pruned.shape[0],
            "reduction_pct": round(1 - (pruned.shape[0] / original_count), 4),
            "quantized_shape": list(quantized.shape),
            "scale": scale,
            "zero_point": zero_point,
        })

    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)

    return {
        "latency_ms": elapsed_ms,
        "target_latency_ms": TARGET_LATENCY_MS,
        "target_footprint_reduction": TARGET_FOOTPRINT_REDUCTION,
        "batches": results,
    }
@router.post("/compare")
def compare_pruning_methods():
    """
    Compares heuristic (similarity-only, 78% baseline) vs
    learned (trained neural scorer) pruning on the same dummy data.
    """
    patches = generate_dummy_patch_embeddings()
    original_count = patches.shape[1]
    single_batch = patches[0]  # [num_patches, dim]

    # Method 1: Heuristic (existing similarity-based)
    pruned_list, keep_mask_heuristic = prune_patches(patches)
    heuristic_kept = pruned_list[0].shape[0]
    heuristic_reduction = 1 - (heuristic_kept / original_count)

    # Method 2: Learned (trained neural scorer)
    keep_mask_learned = learned_prune(single_batch)
    learned_kept = keep_mask_learned.sum().item()
    learned_reduction = 1 - (learned_kept / original_count)

    return {
        "original_patches": original_count,
        "without_edge_pali": {
            "patches_kept": original_count,
            "reduction_pct": 0.0,
            "description": "Raw ColPali output, no optimization"
        },
        "with_edge_pali_heuristic": {
            "patches_kept": heuristic_kept,
            "reduction_pct": round(heuristic_reduction, 4),
            "description": "Similarity-based pruning"
        },
        "with_edge_pali_learned": {
            "patches_kept": learned_kept,
            "reduction_pct": round(learned_reduction, 4),
            "description": "Trained neural network pruning (fast inference)"
        }
    }