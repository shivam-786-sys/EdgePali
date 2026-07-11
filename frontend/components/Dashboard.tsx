"use client";

import { useEffect, useState } from "react";
import MetricCard from "./MetricCard";
import VectorVisualizer from "./VectorVisualizer";

type BatchResult = {
  batch_index: number;
  original_patches: number;
  pruned_patches: number;
  reduction_pct: number;
};

type PruneResponse = {
  latency_ms: number;
  target_latency_ms: number;
  target_footprint_reduction: number;
  batches: BatchResult[];
};

const API_URL = "http://127.0.0.1:8000/prune";

export default function Dashboard() {
  const [data, setData] = useState<PruneResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runPipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_URL, { method: "POST" });
      if (!res.ok) throw new Error("Backend request failed");
      const json: PruneResponse = await res.json();
      setData(json);
    } catch (err) {
      setError("Could not reach backend. Is uvicorn running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runPipeline();
  }, []);

  const firstBatch = data?.batches?.[0];
  const avgReduction =
    data?.batches?.length
      ? data.batches.reduce((sum, b) => sum + b.reduction_pct, 0) / data.batches.length
      : 0;

  return (
    <div className="flex flex-col items-center gap-8 w-full">
      <button
        onClick={runPipeline}
        disabled={loading}
        className="bg-amdred hover:bg-neonorange transition-colors text-white font-mono px-6 py-2 rounded-md disabled:opacity-50"
      >
        {loading ? "Running..." : "Run Pipeline"}
      </button>

      {error && <p className="text-neonorange font-mono">{error}</p>}

      {data && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl">
            <MetricCard label="Latency" value={data.latency_ms} unit="ms" accent="red" />
            <MetricCard
              label="Footprint Reduction"
              value={(avgReduction * 100).toFixed(1)}
              unit="%"
              accent="orange"
            />
            <MetricCard
              label="Original Patches"
              value={firstBatch?.original_patches ?? 0}
              accent="red"
            />
            <MetricCard
              label="Pruned Patches"
              value={firstBatch?.pruned_patches ?? 0}
              accent="orange"
            />
          </div>

          <VectorVisualizer
            key={firstBatch?.pruned_patches}
            originalCount={firstBatch?.original_patches ?? 0}
            prunedCount={firstBatch?.pruned_patches ?? 0}
          />
        </>
      )}
    </div>
  );
}