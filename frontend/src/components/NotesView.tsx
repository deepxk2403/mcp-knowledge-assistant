import { useEffect, useState } from "react";
import {
  createNote,
  deleteNote,
  listNotes,
  searchNotes,
  updateNote,
} from "../api";
import type { Note } from "../types";

const empty = { title: "", content: "", tags: "" };

export default function NotesView() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState<Note | null>(null);
  const [draft, setDraft] = useState(empty);
  const [showEditor, setShowEditor] = useState(false);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const data = query.trim()
        ? await searchNotes(query.trim())
        : await listNotes();
      setNotes(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openNew() {
    setEditing(null);
    setDraft(empty);
    setShowEditor(true);
  }

  function openEdit(n: Note) {
    setEditing(n);
    setDraft({ title: n.title, content: n.content, tags: n.tags || "" });
    setShowEditor(true);
  }

  async function save() {
    if (!draft.title.trim() || !draft.content.trim()) return;
    if (editing) {
      await updateNote(editing.id, draft);
    } else {
      await createNote(draft);
    }
    setShowEditor(false);
    refresh();
  }

  async function remove(id: string) {
    if (!confirm("Delete this note?")) return;
    try {
      await deleteNote(id);
      setNotes((current) => current.filter((note) => note.id !== id));
      await refresh();
    } catch (error) {
      console.error("Failed to delete note", error);
      alert("Failed to delete note. Please try again.");
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-6 py-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && refresh()}
          placeholder="Search notes by meaning…"
          className="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
        />
        <button
          onClick={refresh}
          className="rounded-lg border border-gray-300 px-3 py-2 hover:bg-gray-50"
        >
          Search
        </button>
        {query && (
          <button
            onClick={() => {
              setQuery("");
              setTimeout(refresh, 0);
            }}
            className="rounded-lg border border-gray-300 px-3 py-2 hover:bg-gray-50"
          >
            Clear
          </button>
        )}
        <button
          onClick={openNew}
          className="rounded-lg bg-brand px-3 py-2 text-white"
        >
          + New
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {loading && <div className="text-gray-400">Loading…</div>}
        {!loading && notes.length === 0 && (
          <div className="mt-20 text-center text-gray-400">
            No notes yet. Create one or ask the assistant to save something.
          </div>
        )}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {notes.map((n) => (
            <div
              key={n.id}
              className="flex flex-col rounded-xl border border-gray-200 bg-white p-4"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{n.title}</h3>
                {n.score != null && (
                  <span className="text-xs text-gray-400">
                    {Number(n.score).toFixed(2)}
                  </span>
                )}
              </div>
              <p className="mt-1 flex-1 whitespace-pre-wrap text-sm text-gray-600">
                {n.content}
              </p>
              {n.tags && (
                <div className="mt-2 text-xs text-brand">
                  {n.tags
                    .split(",")
                    .filter(Boolean)
                    .map((t) => `#${t.trim()}`)
                    .join(" ")}
                </div>
              )}
              <div className="mt-3 flex gap-2 text-sm">
                <button
                  onClick={() => openEdit(n)}
                  className="rounded border border-gray-300 px-2 py-1 hover:bg-gray-50"
                >
                  Edit
                </button>
                <button
                  onClick={() => remove(n.id)}
                  className="rounded border border-red-200 px-2 py-1 text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showEditor && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-5">
            <h2 className="mb-3 text-lg font-semibold">
              {editing ? "Edit note" : "New note"}
            </h2>
            <input
              value={draft.title}
              onChange={(e) => setDraft({ ...draft, title: e.target.value })}
              placeholder="Title"
              className="mb-2 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
            />
            <textarea
              value={draft.content}
              onChange={(e) => setDraft({ ...draft, content: e.target.value })}
              placeholder="Content"
              rows={6}
              className="mb-2 w-full resize-none rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
            />
            <input
              value={draft.tags}
              onChange={(e) => setDraft({ ...draft, tags: e.target.value })}
              placeholder="Tags (comma separated)"
              className="mb-4 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowEditor(false)}
                className="rounded-lg border border-gray-300 px-3 py-2 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={save}
                disabled={!draft.title.trim() || !draft.content.trim()}
                className="rounded-lg bg-brand px-3 py-2 text-white disabled:opacity-40"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
