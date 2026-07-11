"use client";

import { useState } from "react";
import MetricCard from "./MetricCard";

const API_URL = "http://127.0.0.1:8000/compare";

export default function ComparisonView() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runCompare = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL, { method: "POST" });
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <button
        onClick={runCompare}
        disabled={loading}
        className="bg-amdred hover:bg-neonorange transition-colors text-white font-mono px-6 py-2 rounded-md disabled:opacity-50"
      >
        {loading ? "Comparing..." : "Compare With/Without Edge-Pali"}
      </button>

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-5xl">
          <div className="border border-gray-700 rounded-lg p-5 bg-obsidian-light">
            <h3 className="text-gray-400 text-xs uppercase mb-3">Without Edge-Pali</h3>
            <MetricCard label="Patches Kept" value={data.without_edge_pali.patches_kept} accent="red" />
          </div>

          <div className="border border-amdred/30 rounded-lg p-5 bg-obsidian-light">
            <h3 className="text-amdred text-xs uppercase mb-3">Heuristic Pruning</h3>
            <MetricCard label="Patches Kept" value={data.with_edge_pali_heuristic.patches_kept} accent="red" />
            <MetricCard
              label="Reduction"
              value={(data.with_edge_pali_heuristic.reduction_pct * 100).toFixed(1)}
              unit="%"
              accent="orange"
            />
          </div>

          <div className="border border-neonorange/30 rounded-lg p-5 bg-obsidian-light">
            <h3 className="text-neonorange text-xs uppercase mb-3">Learned Pruning (Fast)</h3>
            <MetricCard label="Patches Kept" value={data.with_edge_pali_learned.patches_kept} accent="orange" />
            <MetricCard
              label="Reduction"
              value={(data.with_edge_pali_learned.reduction_pct * 100).toFixed(1)}
              unit="%"
              accent="orange"
            />
          </div>
        </div>
      )}
    </div>
  );
}