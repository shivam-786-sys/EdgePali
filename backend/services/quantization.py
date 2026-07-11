"""
FP32 -> INT8 quantization engine with scale + zero-point tracking.
Enables asymmetric distance computation (FP32 query vs INT8 registry).
"""

import torch


def compute_scale_zero_point(tensor: torch.Tensor):
    """
    tensor: [N, dim] float32
    returns: (scale: float, zero_point: int)
    """
    qmin, qmax = 0, 255
    t_min = tensor.min()
    t_max = tensor.max()

    scale = (t_max - t_min) / (qmax - qmin)
    scale = torch.clamp(scale, min=1e-8)

    zero_point = qmin - (t_min / scale)
    zero_point = torch.clamp(zero_point.round(), qmin, qmax)

    return scale.item(), int(zero_point.item())


def quantize_tensor(tensor: torch.Tensor, scale: float, zero_point: int) -> torch.Tensor:
    """
    Returns INT8-representable tensor (stored as uint8 in torch, no native int8 unsigned support).
    """
    q = torch.round(tensor / scale) + zero_point
    q = torch.clamp(q, 0, 255)
    return q.to(torch.uint8)


def dequantize_tensor(q_tensor: torch.Tensor, scale: float, zero_point: int) -> torch.Tensor:
    return (q_tensor.to(torch.float32) - zero_point) * scale


def asymmetric_similarity(query_fp32: torch.Tensor, doc_int8: torch.Tensor, scale: float, zero_point: int) -> torch.Tensor:
    """
    query_fp32: [dim] real-time query vector
    doc_int8: [N, dim] quantized document registry
    returns: [N] similarity scores
    """
    doc_dequant = dequantize_tensor(doc_int8, scale, zero_point)
    query_norm = torch.nn.functional.normalize(query_fp32.unsqueeze(0), p=2, dim=-1)
    doc_norm = torch.nn.functional.normalize(doc_dequant, p=2, dim=-1)
    return torch.matmul(doc_norm, query_norm.T).squeeze(-1)