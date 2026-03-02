"use client";
import { useState, useRef, useEffect } from "react";
import { chatWithStylist } from "@/lib/api";

type Message = { role: "user" | "assistant"; content: string };

const SUGGESTIONS = [
  "Minimal earthy brands for a casual brunch",
  "Sustainable swimwear under ₹3000",
  "Bold prints for a beach vacation in Goa",
  "Handcrafted Indian brands for gifting",
];

export default function StylistPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm Drape ✨ — your AI fashion stylist for indie Indian brands.\n\nTell me what you're looking for — an occasion, a vibe, a budget — and I'll find the perfect brands for you.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text?: string) {
    const msg = text ?? input;
    if (!msg.trim() || loading) return;

    const userMsg: Message = { role: "user", content: msg };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      // Pass history excluding the initial greeting
      const history = updated.slice(1).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const userId =
        typeof window !== "undefined"
          ? Number(localStorage.getItem("user_id")) || undefined
          : undefined;

      const data = await chatWithStylist(msg, history, userId);
      setMessages([
        ...updated,
        { role: "assistant", content: data.reply ?? "Sorry, I couldn't get a response." },
      ]);
    } catch {
      setMessages([
        ...updated,
        {
          role: "assistant",
          content: "⚠️ Couldn't connect to the stylist. Make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-2xl mx-auto">
      {/* Header */}
      <div className="px-4 pt-4 pb-2 border-b">
        <h1 className="text-xl font-bold">✨ AI Stylist</h1>
        <p className="text-xs text-gray-500">Powered by Drape · Indie Indian fashion</p>
      </div>

      {/* Message thread */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`px-4 py-3 rounded-2xl max-w-[85%] text-sm whitespace-pre-wrap leading-relaxed ${
                msg.role === "user"
                  ? "bg-black text-white rounded-br-sm"
                  : "bg-gray-100 text-gray-900 rounded-bl-sm"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-500 px-4 py-3 rounded-2xl rounded-bl-sm text-sm">
              <span className="animate-pulse">Drape is thinking...</span>
            </div>
          </div>
        )}

        {/* Suggestion chips — only show when no conversation yet */}
        {messages.length === 1 && !loading && (
          <div className="flex flex-wrap gap-2 mt-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="text-xs border border-gray-300 rounded-full px-3 py-1.5 hover:bg-gray-50 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="px-4 py-3 border-t bg-white">
        <div className="flex gap-2">
          <input
            className="flex-1 border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            placeholder="Describe your style or occasion..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="bg-black text-white px-4 py-2.5 rounded-xl text-sm font-medium disabled:opacity-40 hover:bg-gray-800 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
