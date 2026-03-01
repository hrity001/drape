"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { registerUser } from "@/lib/api";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const data = await registerUser(form.email, form.password, form.name);
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_id", String(data.user_id));
      localStorage.setItem("has_completed_quiz", String(data.has_completed_quiz));
      router.push("/quiz");
    } else {
      setError(data.detail || "Registration failed");
    }
    setLoading(false);
  };

  return (
    <main className="max-w-sm mx-auto p-6 pt-16 space-y-6">
      <h1 className="text-3xl font-bold text-center">👗 Join Drape</h1>
      <p className="text-center text-gray-500 text-sm">Discover indie fashion brands you'll love</p>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input className="w-full border rounded-xl px-3 py-2 text-sm" placeholder="Your name"
          value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
        <input className="w-full border rounded-xl px-3 py-2 text-sm" placeholder="Email" type="email" required
          value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
        <input className="w-full border rounded-xl px-3 py-2 text-sm" placeholder="Password" type="password" required
          value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button type="submit" disabled={loading}
          className="w-full bg-pink-500 text-white py-2 rounded-xl font-medium">
          {loading ? "Creating account..." : "Create Account"}
        </button>
      </form>
      <p className="text-center text-sm text-gray-500">
        Already have an account? <Link href="/login" className="text-pink-500 underline">Log in</Link>
      </p>
    </main>
  );
}
