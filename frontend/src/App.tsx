import { useEffect, useState } from "react";
import type { MouseEvent } from "react";
import { deleteSession, listSessions } from "./api";
import ChatView from "./components/ChatView";
import NotesView from "./components/NotesView";
import type { Session } from "./types";

type Tab = "chat" | "notes";

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<string | null>(null);

  async function refreshSessions() {
    try {
      setSessions(await listSessions());
    } catch {
      setSessions([]);
    }
  }

  useEffect(() => {
    refreshSessions();
  }, []);

  function newChat() {
    setActiveSession(null);
    setTab("chat");
  }

  async function removeSession(id: string, e: MouseEvent) {
    e.stopPropagation();
    await deleteSession(id);
    if (activeSession === id) setActiveSession(null);
    refreshSessions();
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-gray-200 bg-white">
        <div className="px-4 py-4">
          <div className="text-lg font-bold text-brand">🧠 Knowledge</div>
          <div className="text-xs text-gray-400">MCP Assistant</div>
        </div>

        <div className="flex gap-1 px-3">
          <button
            onClick={() => setTab("chat")}
            className={`flex-1 rounded-lg px-3 py-1.5 text-sm ${
              tab === "chat" ? "bg-brand text-white" : "hover:bg-gray-100"
            }`}
          >
            Chat
          </button>
          <button
            onClick={() => setTab("notes")}
            className={`flex-1 rounded-lg px-3 py-1.5 text-sm ${
              tab === "notes" ? "bg-brand text-white" : "hover:bg-gray-100"
            }`}
          >
            Notes
          </button>
        </div>

        {tab === "chat" && (
          <>
            <div className="px-3 pt-3">
              <button
                onClick={newChat}
                className="w-full rounded-lg border border-brand/40 px-3 py-1.5 text-sm text-brand hover:bg-brand/5"
              >
                + New chat
              </button>
            </div>
            <div className="mt-2 flex-1 overflow-y-auto px-2">
              {sessions.map((s) => (
                <div
                  key={s.id}
                  onClick={() => {
                    setActiveSession(s.id);
                    setTab("chat");
                  }}
                  className={`group flex cursor-pointer items-center justify-between rounded-lg px-2 py-1.5 text-sm ${
                    activeSession === s.id
                      ? "bg-brand/10 text-brand"
                      : "hover:bg-gray-100"
                  }`}
                >
                  <span className="truncate">{s.title}</span>
                  <button
                    onClick={(e) => removeSession(s.id, e)}
                    className="ml-1 hidden text-gray-400 hover:text-red-500 group-hover:block"
                  >
                    ✕
                  </button>
                </div>
              ))}
              {sessions.length === 0 && (
                <div className="px-2 py-2 text-xs text-gray-400">
                  No chats yet.
                </div>
              )}
            </div>
          </>
        )}
        <div className="border-t border-gray-100 px-4 py-2 text-[11px] text-gray-400">
          Free stack · OpenRouter + FastEmbed
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-hidden">
        {tab === "chat" ? (
          <ChatView
            key={activeSession || "new"}
            sessionId={activeSession}
            onSessionCreated={(s) => {
              setActiveSession(s.id);
              refreshSessions();
            }}
            onActivity={refreshSessions}
          />
        ) : (
          <NotesView />
        )}
      </main>
    </div>
  );
}
