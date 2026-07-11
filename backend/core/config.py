# Global constants and threshold limits for Edge-Pali

# Mock tensor shape config (mimics ColPali-style multi-vector output)
BATCH_SIZE = 4
NUM_PATCHES = 1024
EMBEDDING_DIM = 128

# Pruning thresholds
SIMILARITY_THRESHOLD = 0.92      # patches above this similarity are candidates for pruning
VARIANCE_SAFETY_THRESHOLD = 0.05  # tau: min entropy contribution to survive pruning

# Quantization config
QUANT_DTYPE_BITS = 8

# Performance targets (for reporting/metrics only)
TARGET_FOOTPRINT_REDUCTION = 0.75
TARGET_LATENCY_MS = 800
TARGET_RECALL_DROP_MAX = 0.02