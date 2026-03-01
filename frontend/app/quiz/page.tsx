"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { embedText, savePreferenceVector } from "@/lib/api";

const questions = [
  {
    id: "vibe",
    question: "What's your style vibe?",
    options: ["Minimal & Clean", "Bold & Colorful", "Earthy & Sustainable", "Streetwear & Urban"],
  },
  {
    id: "budget",
    question: "What's your usual budget per outfit?",
    options: ["Under ₹1,000", "₹1,000 – ₹3,000", "₹3,000 – ₹8,000", "₹8,000+"],
  },
  {
    id: "category",
    question: "What do you shop for most?",
    options: ["Everyday Casual", "Swimwear & Beachwear", "Workwear", "Occasion & Festive Wear"],
  },
  {
    id: "location",
    question: "Where are you based?",
    options: ["India", "Southeast Asia", "Europe / US", "Other"],
  },
  {
    id: "values",
    question: "What matters most to you in a brand?",
    options: ["Sustainability", "Uniqueness & Indie", "Affordable Price", "Brand Story & Craft"],
  },
];

export default function QuizPage() {
  const router = useRouter();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const allAnswered = questions.every(q => answers[q.id]);

  const handleSubmit = async () => {
    setLoading(true);
    const userId = Number(localStorage.getItem("user_id"));

    // Combine answers into a rich text string for embedding
    const text = [
      `Style vibe: ${answers.vibe}`,
      `Budget: ${answers.budget}`,
      `Shopping category: ${answers.category}`,
      `Location: ${answers.location}`,
      `Brand values: ${answers.values}`,
    ].join(". ");

    const { embedding } = await embedText(text);
    await savePreferenceVector(userId, embedding);

    localStorage.setItem("has_completed_quiz", "true");
    router.push("/");
  };

  return (
    <main className="max-w-md mx-auto p-6 space-y-8 pb-24">
      <div className="text-center space-y-1 pt-6">
        <h1 className="text-2xl font-bold">👗 Let's find your style</h1>
        <p className="text-gray-500 text-sm">Answer 5 quick questions to personalize your feed</p>
      </div>

      {questions.map((q, qi) => (
        <div key={q.id} className="space-y-3">
          <p className="font-semibold text-sm">
            {qi + 1}. {q.question}
          </p>
          <div className="grid grid-cols-2 gap-2">
            {q.options.map(opt => (
              <button
                key={opt}
                onClick={() => setAnswers(a => ({ ...a, [q.id]: opt }))}
                className={`py-2 px-3 rounded-xl text-sm border transition-all ${
                  answers[q.id] === opt
                    ? "bg-pink-500 text-white border-pink-500 font-medium"
                    : "bg-white text-gray-700 border-gray-200 hover:border-pink-300"
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}

      <button
        onClick={handleSubmit}
        disabled={!allAnswered || loading}
        className={`w-full py-3 rounded-xl font-semibold text-white transition-all ${
          allAnswered && !loading ? "bg-pink-500" : "bg-gray-300 cursor-not-allowed"
        }`}
      >
        {loading ? "Finding your brands..." : "Show My Brands ✨"}
      </button>
    </main>
  );
}
