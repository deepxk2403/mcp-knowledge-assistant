import type { ChatEvent, Message, Note, Session } from "./types";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} ${text}`);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

// Always hit the network for reads — never let the browser serve a stale
// cached list (e.g. after a delete). "no-store" disables HTTP caching.
const GET = (url: string) => fetch(url, { cache: "no-store" });

// --- Notes ---
export const listNotes = () => GET("/notes").then((r) => json<Note[]>(r));

export const searchNotes = (q: string) =>
  GET(`/notes/search?q=${encodeURIComponent(q)}&top_k=10`).then((r) =>
    json<Note[]>(r)
  );

export const createNote = (body: {
  title: string;
  content: string;
  tags?: string;
}) =>
  fetch("/notes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((r) => json<Note>(r));

export const updateNote = (
  id: string,
  body: { title?: string; content?: string; tags?: string }
) =>
  fetch(`/notes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((r) => json<Note>(r));

export const deleteNote = (id: string) =>
  fetch(`/notes/${id}`, { method: "DELETE" }).then((r) => json<void>(r));

// --- Sessions / history ---
export const listSessions = () =>
  GET("/sessions").then((r) => json<Session[]>(r));

export const getMessages = (sessionId: string) =>
  GET(`/sessions/${sessionId}/messages`).then((r) => json<Message[]>(r));

export const deleteSession = (sessionId: string) =>
  fetch(`/sessions/${sessionId}`, { method: "DELETE" }).then((r) =>
    json<void>(r)
  );

// --- Streaming chat (SSE over POST) ---
export async function streamChat(
  message: string,
  sessionId: string | null,
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const line = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!line) continue;
      try {
        onEvent(JSON.parse(line.slice(5).trim()) as ChatEvent);
      } catch {
        /* ignore malformed frame */
      }
    }
  }
}
