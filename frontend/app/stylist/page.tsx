"use client";
import { useState } from "react";
import { searchBrands, submitFeedback } from "@/lib/api";
import BrandCard from "@/components/BrandCard";

const USER_ID = 1; // hardcoded until auth is added

export default function StylistPage() {
  const [query, setQuery] = useState("");
  const [brands, setBrands] = useState<any[]>([]);
  const [index, setIndex] = useState(0);

  const handleSearch = async () => {
    const results = await searchBrands(query);
    setBrands(results); setIndex(0);
  };

  const current = brands[index];

  return (
    <main className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">🤖 AI Stylist</h1>
      <div className="flex gap-2">
        <input className="flex-1 border rounded-xl px-3 py-2 text-sm"
          placeholder="Describe your style..."
          value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()} />
        <button onClick={handleSearch} className="bg-pink-500 text-white px-4 rounded-xl text-sm">Ask</button>
      </div>
      {current ? (
        <BrandCard brand={current}
          onLike={async () => { await submitFeedback(USER_ID, current.id, true); setIndex(i => i + 1); }}
          onDislike={() => setIndex(i => i + 1)} />
      ) : brands.length > 0 ? (
        <p className="text-center text-gray-500">No more brands! Try a new search.</p>
      ) : null}
    </main>
  );
}
