<div align="center">

# 🗜️ Edge-Pali

### Dynamic VRAM Optimization and Patch Pruning for Vision-Language Models on Edge Devices

</div>

---

## The Problem

Advanced Vision-Language Models (like ColPali) process documents differently than traditional OCR. Instead of just extracting text, they break a page into visual "patches" and generate a heavy mathematical vector for each one (around 1,030 vectors per page). This is brilliant for understanding complex layouts, charts, and infographics, but it creates a massive storage problem. 

A document store of just 10,000 pages balloons into 10M+ vectors, requiring over 5.3GB of VRAM just for the embeddings. On edge devices, robotics platforms, or cost-constrained hardware, this makes deploying state-of-the-art visual retrieval completely impractical.
## The solution
**Edge-Pali solves this by acting like a smart filter.** It recognizes that not every part of a document is equally important. Blank margins, solid backgrounds, and repetitive spaces are algorithmically identified and discarded before storage. By aggressively pruning redundant patches and compressing the rest, Edge-Pali drastically shrinks the memory footprint while maintaining the layout-aware brilliance of the original model.

---

## What Makes This Different

Standard deployment approaches assume infinite cloud resources. Edge-Pali is built for the reality of edge constraints.

| Stage | Standard Approach | This System |
|---|---|---|
| **Patch Retention** | All patches stored, no filtering | Learned + heuristic pruning removes redundant/low-information patches |
| **Precision** | FP32 vectors stored as-is | INT8 quantization with scale/zero-point, asymmetric FP32↔INT8 matching at query time |
| **Pruning Decision** | N/A (no pruning stage exists) | Dual-path: O(N²) similarity heuristic (validated ceiling) + distilled neural scorer (single forward pass, faster inference) |
| **Deployment Target** | Cloud / high-VRAM only | Designed specifically for edge / resource-constrained inference |
| **File Input** | Pre-processed embeddings assumed | Real-time PDF/image ingestion via PyMuPDF + live ColPali inference |

---

## System Architecture

                        ┌─────────────────────┐
                        │   File Upload (UI)   │
                        │   PDF / PNG / JPG     │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  FastAPI /process-    │
                        │  document endpoint    │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  PyMuPDF (PDF→Image)  │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  ColPali (vidore/     │
                        │  colpali-v1.3)        │
                        │  → [N patches, 128]   │
                        └──────────┬───────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
       ┌──────────▼──────────┐           ┌───────────▼───────────┐
       │ Similarity Heuristic │          │  Trained NN Scorer    │
       │  (cosine sim, O(N²)) │          │  (PatchImportanceScorer│
       │  Teacher / baseline   │          │  best_scorer.pt)       │
       └──────────┬──────────┘           └───────────┬───────────┘
                  └────────────────┬────────────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  INT8 Quantization    │
                        │  (scale + zero-point) │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  Next.js Dashboard    │
                        │  Without vs With UI   │
                        └───────────────────────┘

---

## Core Technical Components

### 1. Backend Inference Engine (FastAPI + PyTorch)
The `/process-document` endpoint is built for lightweight startup. It lazy-loads the massive 5.85GB ColPali model only on the first request to avoid blocking server boot times. Uploaded PDFs are instantly converted to RGB images (rendered at 150 DPI via PyMuPDF), passed through ColPali's vision-language encoder to generate per-patch embeddings, and then routed through the pruning pipeline. The API returns a split-response: the unmodified baseline and the pruned/quantized result, allowing the frontend to display a real-time comparison.

### 2. Dual-Path Compression (Pruning + INT8 Quantization)
The system utilizes two distinct pruning methodologies:
*   **The Heuristic Path (Teacher):** Computes a full patch-to-patch cosine similarity matrix, flagging patches above a 0.92 similarity threshold as redundant. This serves as our empirically validated ceiling, achieving a 78.01% reduction across benchmark datasets.
*   **The Learned Path (Student):** Uses a distilled 3-layer neural network (`PatchImportanceScorer`, ~10K parameters) trained via knowledge distillation against the heuristic's labels. It trades a fraction of accuracy for O(1) inference speed (a single forward pass) instead of the heuristic's O(N²) complexity, which is critical for real-time edge processing.

Surviving patches are quantized from FP32 to INT8 using per-tensor scale and zero-point calculations. Asymmetric distance computation allows new FP32 search queries to match against the INT8 registry without requiring full memory-heavy dequantization.

### 3. Asymmetric Dashboard (Next.js)
The UI doesn't just show the result; it proves the optimization. The dashboard features an asymmetric split view: a left panel showing the unmodified baseline (original patch count, storage size, 100% reference accuracy) and a larger right panel displaying the Edge-Pali optimized result. It explicitly displays an "Honest Tradeoff Accuracy" metric, showing exactly how much VRAM was saved and the minimal impact on retrieval quality.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Deep Learning** | PyTorch, ColPali (`vidore/colpali-v1.3`), custom `PatchImportanceScorer` |
| **Data Ingestion** | PyMuPDF (PDF→image extraction), Pillow |
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **Frontend** | Next.js 16 (Turbopack), TypeScript, Tailwind CSS v4, Framer Motion |
| **Deployment** | Docker (multi-container orchestration), Docker-Compose |

---

## Pipeline Status

| Phase | Status |
|---|---|
| Backend scaffold + dummy pipeline | ✅ Complete |
| Real ColPali validation (heuristic, 9,700 images) | ✅ Complete |
| Learned pruning model (training) | ✅ Complete |
| Frontend dashboard (dummy pipeline) | ✅ Complete |
| Real file upload + live inference endpoint | ✅ Complete |
| Frontend Without/With comparison UI | ✅ Complete |
| End-to-end verified on local (9,700 images) | ✅ Complete |

*Note: Future development involves training the neural scorer on a massively scaled and diverse dataset to further bridge the accuracy gap between the O(N²) heuristic model and the O(1) learned model.*

---

## Performance & Optimization Data

**Heuristic Baseline** 
*(Similarity-threshold pruning, τ=0.92, validated across ~9,700 real document images spanning 10 domains including arXiv, DocVQA, TAT-DQA, and infographics)*
*   **Average VRAM/Vector Reduction:** **78.01%**
*   **Representation Similarity Retained:** **~99.36%** *(Single-document proxy measurement)*

**Trained Student Model (`best_scorer.pt`)** 
*(Distilled via knowledge distillation from the heuristic. Trained on 7,598 images / Validated on 845 held-out unseen images)*
*   **Final Training Loss:** **0.5798**
*   **Agreement with Heuristic Teacher (Unseen Data):** **67.17%**
*   **Average Reduction Achieved (Unseen Data):** **46.32%**
*   **Inference Speed:** **Single O(1) forward pass** *(No O(N²) similarity matrix required at query time)*.

**Honest Framing:** The student model's reduction numbers are currently lower than the heuristic ceiling. We explicitly disclose this rather than obscuring it. The student model's true value proposition is its uncompromised inference speed for real-time edge scenarios, trading maximum compression for computational velocity.

---

### 📊 Performance & Evaluation Results

We evaluated Edge-Pali on complex technical documentation to verify VRAM efficiency and model parity.

<div align="center">

| Model/Paper | Input Type | VRAM Optimization | Result Preview |
| :--- | :--- | :--- | :--- |
| **LSTM Architecture** | 2-page Technical PDF | ~81.6% Reduction | <img width="935" height="515" alt="Image" src="https://github.com/user-attachments/assets/b89604d8-a3b9-4f09-ae8e-25c99357d8ae" />|
| **Transformer (Attention Is All You Need)** | 11-page Research Paper | ~80.4% Reduction |<img width="934" height="503" alt="Image" src="https://github.com/user-attachments/assets/2b432d79-adbe-47cf-a2aa-fdcfd0631e75" /> |

</div>

## Screenshots & Localhost Visualization

<img width="1600" height="864" alt="Image" src="https://github.com/user-attachments/assets/09e83ad2-0b40-4a31-a6ca-9723268b0465" />
<img width="1600" height="907" alt="Image" src="https://github.com/user-attachments/assets/b51f32f5-51e6-40ae-a61d-fb9d6aba0601" />


