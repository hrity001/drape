"use client";
import { useState, useEffect } from "react";
import { getBrands, searchBrands } from "@/lib/api";
import BrandCard from "@/components/BrandCard";

export default function DiscoverPage() {
  const [brands, setBrands] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => { getBrands().then(setBrands); }, []);

  const handleSearch = async () => {
    if (query.trim()) setBrands(await searchBrands(query));
  };

  return (
    <main className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">🔍 Discover Brands</h1>
      <div className="flex gap-2">
        <input className="flex-1 border rounded-xl px-3 py-2 text-sm"
          placeholder="e.g. sustainable swimwear India"
          value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()} />
        <button onClick={handleSearch} className="bg-pink-500 text-white px-4 rounded-xl text-sm">Search</button>
      </div>
      {brands.map((b: any) => <BrandCard key={b.id} brand={b} />)}
    </main>
  );
}
