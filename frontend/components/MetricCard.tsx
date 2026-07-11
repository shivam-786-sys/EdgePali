type MetricCardProps = {
  label: string;
  value: string | number;
  unit?: string;
  accent?: "red" | "orange";
};

export default function MetricCard({
  label,
  value,
  unit = "",
  accent = "red",
}: MetricCardProps) {
  const accentColor = accent === "red" ? "text-amdred" : "text-neonorange";
  const borderColor = accent === "red" ? "border-amdred/30" : "border-neonorange/30";

  return (
    <div
      className={`bg-obsidian-light border ${borderColor} rounded-lg p-5 flex flex-col gap-1 shadow-lg`}
    >
      <span className="text-gray-400 text-xs uppercase tracking-wider font-sans">
        {label}
      </span>
      <span className={`font-mono text-2xl font-bold ${accentColor}`}>
        {value}
        {unit && <span className="text-sm ml-1 text-gray-500">{unit}</span>}
      </span>
    </div>
  );
}