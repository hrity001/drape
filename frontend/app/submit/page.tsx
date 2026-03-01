"use client";
import { useState } from "react";
import { submitBrand } from "@/lib/api";

export default function SubmitPage() {
  const [form, setForm] = useState({ name: "", website: "", instagram_handle: "", description: "" });
  const [done, setDone] = useState(false);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    await submitBrand(form);
    setDone(true);
  };

  return (
    <main className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">📝 Submit Your Brand</h1>
      {done ? <p className="text-green-600">✅ Submitted! We'll review it soon.</p> : (
        <form onSubmit={handleSubmit} className="space-y-3">
          {["name","website","instagram_handle","description"].map(field => (
            <input key={field} required={field === "name"}
              className="w-full border rounded-xl px-3 py-2 text-sm"
              placeholder={field.replace("_", " ")}
              value={(form as any)[field]}
              onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))} />
          ))}
          <button type="submit" className="w-full bg-pink-500 text-white py-2 rounded-xl">Submit Brand</button>
        </form>
      )}
    </main>
  );
}
