import { useEffect, useRef, useState } from "react";
import { getMessages, streamChat } from "../api";
import type { Citation, Message, Session } from "../types";
import CitationChips from "./CitationChips";

interface Props {
  sessionId: string | null;
  onSessionCreated: (s: Session) => void;
  onActivity: () => void;
}

// Render plain text: drop the model's raw 【id】 markers (sources show as chips)
// and turn **bold** into <strong>.
function renderText(text: string) {
  const clean = text.replace(/【[^】]*】/g, "");
  const parts = clean.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={i}>{p.slice(2, -2)}</strong>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}

export default function ChatView({
  sessionId,
  onSessionCreated,
  onActivity,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setError(null);
    if (sessionId) {
      getMessages(sessionId).then(setMessages).catch(() => setMessages([]));
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setError(null);
    setBusy(true);

    const userMsg: Message = {
      id: crypto.randomUUID(),
      session_id: sessionId || "",
      role: "user",
      content: text,
      citations: [],
      created_at: "",
    };
    // Optimistic user message + an empty assistant placeholder to fill in.
    const assistantId = crypto.randomUUID();
    setMessages((m) => [
      ...m,
      userMsg,
      {
        id: assistantId,
        session_id: sessionId || "",
        role: "assistant",
        content: "",
        citations: [],
        created_at: "",
      },
    ]);

    const citations: Citation[] = [];
    let answer = "";
    let newSession: Session | null = null;

    try {
      await streamChat(text, sessionId, (e) => {
        if (e.type === "session" && !sessionId) {
          newSession = {
            id: e.id,
            title: e.title,
            created_at: "",
            updated_at: "",
          };
        } else if (e.type === "citation") {
          citations.push(e.data);
        } else if (e.type === "token") {
          answer += e.text;
        } else if (e.type === "error") {
          setError(e.message);
        }
        setMessages((m) =>
          m.map((msg) =>
            msg.id === assistantId
              ? { ...msg, content: answer, citations: [...citations] }
              : msg
          )
        );
      });
      if (newSession) onSessionCreated(newSession);
      onActivity();
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !busy && (
          <div className="mt-20 text-center text-gray-400">
            <div className="text-2xl mb-2">💬</div>
            Ask me to save a note, search your notes, or look something up.
          </div>
        )}
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={m.role === "user" ? "flex justify-end" : "flex justify-start"}
            >
              <div
                className={
                  m.role === "user"
                    ? "max-w-[80%] rounded-2xl bg-brand px-4 py-2 text-white"
                    : "max-w-[80%] rounded-2xl bg-white border border-gray-200 px-4 py-2"
                }
              >
                <div className="whitespace-pre-wrap leading-relaxed">
                  {m.content ? (
                    renderText(m.content)
                  ) : m.role === "assistant" && busy ? (
                    <span className="text-gray-400">thinking…</span>
                  ) : null}
                </div>
                {m.role === "assistant" && (
                  <CitationChips citations={m.citations} />
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      {error && (
        <div className="mx-auto mb-2 max-w-3xl rounded bg-red-50 px-3 py-1.5 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="border-t border-gray-200 bg-white px-6 py-3">
        <div className="mx-auto flex max-w-3xl gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            rows={1}
            placeholder="Message your knowledge assistant…"
            className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
          <button
            onClick={send}
            disabled={busy || !input.trim()}
            className="rounded-xl bg-brand px-4 py-2 text-white disabled:opacity-40"
          >
            {busy ? "…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
