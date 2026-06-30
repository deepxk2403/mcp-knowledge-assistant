import { useState } from "react";
import type { Citation } from "../types";

export default function CitationChips({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState<number | null>(null);
  const withItems = citations.filter((c) => c.items && c.items.length > 0);
  if (withItems.length === 0) return null;

  return (
    <div className="mt-2 space-y-1">
      <div className="flex flex-wrap gap-1.5">
        {withItems.map((c, i) => (
          <button
            key={i}
            onClick={() => setOpen(open === i ? null : i)}
            className="text-xs rounded-full border border-brand/30 bg-brand/5 px-2 py-0.5 text-brand hover:bg-brand/10"
          >
            {c.type === "web" ? "🌐" : "📝"} {c.items.length} source
            {c.items.length > 1 ? "s" : ""}
            {c.query ? ` · "${c.query}"` : ""}
          </button>
        ))}
      </div>
      {open !== null && withItems[open] && (
        <div className="rounded-lg border border-gray-200 bg-white p-2 text-xs space-y-2">
          {withItems[open].items.map((it, j) => (
            <div key={j} className="border-l-2 border-brand/40 pl-2">
              {it.url ? (
                <a
                  href={it.url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-medium text-brand hover:underline"
                >
                  {it.title || it.url}
                </a>
              ) : (
                <div className="font-medium">
                  {it.title || "(untitled)"}
                  {it.score ? (
                    <span className="ml-1 text-gray-400">
                      score {it.score}
                    </span>
                  ) : null}
                </div>
              )}
              <div className="text-gray-600">{it.snippet || it.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
