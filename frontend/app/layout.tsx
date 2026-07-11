import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Edge-Pali | VRAM Optimizer",
  description: "Dynamic multi-vector RAG optimization for edge deployment",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-obsidian text-white font-sans min-h-screen">
        {children}
      </body>
    </html>
  );
}