import Dashboard from "@/components/Dashboard";
import ComparisonView from "@/components/ComparisonView";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-8 gap-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-amdred">Edge-Pali</h1>
        <p className="text-gray-400 mt-2 font-mono">Dynamic VRAM Optimizer</p>
      </div>

      <Dashboard />
      <ComparisonView />
    </main>
  );
}