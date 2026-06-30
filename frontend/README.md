# Frontend — MCP Knowledge Assistant (React)

Vite + React + TypeScript + Tailwind single-page app. Talks to the FastAPI
backend over HTTP/SSE (proxied in dev — see `vite.config.ts`).

## Features

- **Chat** with streaming responses, citation chips (click to expand sources),
  and a sessions sidebar (resume / delete past chats, new chat).
- **Notes** — semantic search, create, edit, delete.

## Run (dev)

Backend must be running first (see `../backend/README.md`): Qdrant, the API
(:8000), and the MCP server (:8001).

```
npm install        # first time only
npm run dev        # http://localhost:3000
```

The Vite dev server proxies `/notes`, `/chat`, `/sessions`, `/health` to the
backend on :8000, so no CORS or env config is needed in development.

## Structure

```
src/
├── api.ts              # typed client + SSE chat stream parser
├── types.ts            # shared types
├── App.tsx             # layout: sidebar + Chat/Notes tabs
└── components/
    ├── ChatView.tsx        # streaming chat
    ├── CitationChips.tsx   # expandable sources
    └── NotesView.tsx       # notes CRUD + search
```

## Build (production)

```
npm run build      # outputs dist/
```
In production, serve `dist/` from any static host and point it at the backend
(replace the dev proxy with a real base URL in `api.ts`, or serve both behind
one reverse proxy).
