"use client";

import { motion } from "framer-motion";

type VectorVisualizerProps = {
  originalCount: number;
  prunedCount: number;
};

export default function VectorVisualizer({
  originalCount,
  prunedCount,
}: VectorVisualizerProps) {
  const displayCount = Math.min(originalCount, 200); // cap for render performance
  const scaleRatio = originalCount > 0 ? prunedCount / originalCount : 1;

  return (
    <div className="bg-obsidian-light border border-amdred/20 rounded-lg p-6 w-full max-w-4xl">
      <span className="text-gray-400 text-xs uppercase tracking-wider font-sans">
        Vector Footprint
      </span>

      <div className="flex flex-wrap gap-1 mt-4 max-h-40 overflow-hidden">
        {Array.from({ length: displayCount }).map((_, i) => {
          const isPruned = i / displayCount > scaleRatio;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 1, scale: 1 }}
              animate={
                isPruned
                  ? { opacity: 0.15, scale: 0.6 }
                  : { opacity: 1, scale: 1 }
              }
              transition={{ duration: 0.5, delay: i * 0.002 }}
              className={`w-3 h-3 rounded-sm ${
                isPruned ? "bg-gray-700" : "bg-amdred"
              }`}
            />
          );
        })}
      </div>

      <div className="flex justify-between mt-4 font-mono text-sm">
        <span className="text-gray-500">Original: {originalCount}</span>
        <span className="text-neonorange">Pruned: {prunedCount}</span>
      </div>
    </div>
  );
}