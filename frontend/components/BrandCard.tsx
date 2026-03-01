type Brand = {
  id: number; name: string; website?: string;
  instagram_handle?: string; country?: string;
  category?: string[]; price_range?: string;
  tags?: string[]; description?: string; score?: number;
};

export default function BrandCard({ brand, onLike, onDislike }: {
  brand: Brand;
  onLike?: () => void;
  onDislike?: () => void;
}) {
  return (
    <div className="rounded-2xl border p-4 shadow-sm bg-white space-y-2">
      <div className="flex justify-between items-start">
        <h2 className="text-lg font-bold">{brand.name}</h2>
        {brand.price_range && (
          <span className="text-xs bg-gray-100 px-2 py-1 rounded-full">{brand.price_range}</span>
        )}
      </div>
      {brand.description && <p className="text-sm text-gray-600">{brand.description}</p>}
      <div className="flex flex-wrap gap-1">
        {brand.tags?.map(t => (
          <span key={t} className="text-xs bg-pink-100 text-pink-700 px-2 py-0.5 rounded-full">{t}</span>
        ))}
      </div>
      <div className="flex gap-3 text-sm">
        {brand.website && <a href={brand.website} target="_blank" className="text-blue-500 underline">Website</a>}
        {brand.instagram_handle && (
          <a href={`https://instagram.com/${brand.instagram_handle}`} target="_blank" className="text-pink-500 underline">Instagram</a>
        )}
      </div>
      {(onLike || onDislike) && (
        <div className="flex gap-3 pt-2">
          <button onClick={onDislike} className="flex-1 py-2 rounded-xl bg-gray-100 text-gray-600">👎 Pass</button>
          <button onClick={onLike} className="flex-1 py-2 rounded-xl bg-pink-500 text-white">❤️ Like</button>
        </div>
      )}
    </div>
  );
}
