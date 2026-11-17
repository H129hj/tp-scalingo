const API_URL = import.meta.env.VITE_API_URL as string | undefined;

export function apiUrl(path: string): string {
  if (!API_URL) throw new Error("VITE_API_URL n'est pas definie");
  return `${API_URL.replace(/\/$/, "")}${path}`;
}

export type Note = { id: number; title: string; body: string; created_at: string };

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(typeof detail.detail === "string" ? detail.detail : `Erreur ${res.status}`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const auth = (mode: "login" | "register", email: string, password: string) =>
  request<{ access_token: string }>(`/auth/${mode}`, { method: "POST", body: JSON.stringify({ email, password }) });
export const listNotes = (t: string) => request<Note[]>("/notes", {}, t);
export const addNote = (t: string, title: string, body: string) =>
  request<Note>("/notes", { method: "POST", body: JSON.stringify({ title, body }) }, t);
export const deleteNote = (t: string, id: number) => request<void>(`/notes/${id}`, { method: "DELETE" }, t);
