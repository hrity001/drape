const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function searchBrands(query: string, filters = {}) {
  const res = await fetch(`${BASE}/search/brands`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, ...filters }),
  });
  return res.json();
}

export async function getBrands() {
  const res = await fetch(`${BASE}/brands/`);
  return res.json();
}

export async function submitFeedback(user_id: number, brand_id: number, liked: boolean) {
  const res = await fetch(`${BASE}/users/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, brand_id, liked }),
  });
  return res.json();
}

export async function submitBrand(data: object) {
  const res = await fetch(`${BASE}/submissions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}
export async function registerUser(email: string, password: string, name: string) {
  const res = await fetch(`${BASE}/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  return res.json();
}

export async function loginUser(email: string, password: string) {
  const res = await fetch(`${BASE}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function embedText(text: string) {
  const res = await fetch(`${BASE}/search/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

export async function savePreferenceVector(userId: number, embedding: number[]) {
  const res = await fetch(`${BASE}/users/${userId}/preference_vector`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ embedding }),
  });
  return res.json();
}
