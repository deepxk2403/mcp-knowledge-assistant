export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string;
  created_at: string;
  updated_at: string;
  score?: number | null;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface CitationItem {
  id?: string | null;
  title?: string;
  snippet?: string;
  score?: string | null;
  url?: string;
  text?: string;
}

export interface Citation {
  tool: string;
  type: "note" | "web" | "generic";
  query: string;
  items: CitationItem[];
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
  created_at: string;
}

export type ChatEvent =
  | { type: "session"; id: string; title: string }
  | { type: "citation"; data: Citation }
  | { type: "token"; text: string }
  | { type: "done"; content: string; citations: Citation[] }
  | { type: "error"; message: string };
