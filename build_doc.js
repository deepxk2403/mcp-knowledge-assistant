const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, Footer, PageBreak
} = require("docx");

// ---------- helpers ----------
const FONT = "Calibri";
const BLUE = "1F4E79";
const GREY = "F2F2F2";

const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, before: opts.before ?? 0, line: 276 },
    alignment: opts.align,
    children: [new TextRun({ text, bold: opts.bold, italics: opts.italics, size: opts.size ?? 22, color: opts.color, font: FONT })],
  });
}

function runs(children, opts = {}) {
  return new Paragraph({ spacing: { after: opts.after ?? 120, line: 276 }, children });
}

function t(text, o = {}) {
  return new TextRun({ text, bold: o.bold, italics: o.italics, size: o.size ?? 22, color: o.color, font: o.font ?? FONT });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bul", level },
    spacing: { after: 60, line: 276 },
    children: Array.isArray(text) ? text : [new TextRun({ text, size: 22, font: FONT })],
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: "num", level: 0 },
    spacing: { after: 80, line: 276 },
    children: Array.isArray(text) ? text : [new TextRun({ text, size: 22, font: FONT })],
  });
}

function code(text) {
  return new Paragraph({
    spacing: { after: 60, before: 60 },
    shading: { fill: GREY, type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: "Consolas", size: 19 })],
  });
}

function cell(content, { w, fill, header } = {}) {
  const kids = Array.isArray(content) ? content : [new Paragraph({
    spacing: { after: 0, line: 264 },
    children: [new TextRun({ text: content, bold: header, size: 20, color: header ? "FFFFFF" : "000000", font: FONT })],
  })];
  return new TableCell({
    borders,
    width: { size: w, type: WidthType.DXA },
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: kids,
  });
}

function table(widths, rows) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) =>
      new TableRow({
        children: r.map((c, ci) =>
          cell(c, { w: widths[ci], fill: ri === 0 ? BLUE : (ri % 2 === 0 ? GREY : undefined), header: ri === 0 })
        ),
      })
    ),
  });
}

const H = (text) =>
  new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: [new TextRun({ text, font: FONT })] });

// ---------- document ----------
const children = [];

// Title block
children.push(new Paragraph({
  spacing: { after: 60, before: 600 },
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "Personal Knowledge Assistant", bold: true, size: 48, color: BLUE, font: FONT })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 40 },
  children: [new TextRun({ text: "A Custom MCP-Powered Web App — Explained from Scratch", size: 26, color: "555555", font: FONT })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 320 },
  children: [new TextRun({ text: "Chat · Notes · Web Search · Citations · History", italics: true, size: 22, color: "777777", font: FONT })],
}));

// 1. What is this
children.push(H("1. What Is This Project?"));
children.push(p("This is a web app you talk to like a chat assistant. It has two superpowers:"));
children.push(bullet("A memory — it saves your notes and finds them by meaning, not just exact words."));
children.push(bullet("Web access — it can search the live internet when you ask about current information."));
children.push(p("It started as a terminal program and has grown into a real product: a browser interface where you chat, manage notes, see live answers stream in, and view the exact sources behind every answer."));
children.push(p("The engine underneath uses a standard called MCP (Model Context Protocol). Instead of cramming everything into one program, the abilities live in a separate “toolbox” server, and the AI “brain” plugs into it. The brain asks “what can you do?” and uses whatever tools it finds — so either side can be swapped without rewriting the other.", { italics: true }));

// 2. Building blocks
children.push(H("2. The Building Blocks, in Plain Words"));
children.push(p("A few terms appear throughout. Here is what each one really means:"));
children.push(table([2350, 7010], [
  ["Term", "What it means (simple version)"],
  ["LLM / AI model", "The “brain” — a large language model (here a free model via OpenRouter) that reads your text, decides what to do, and writes replies."],
  ["Agent", "The brain plus a loop: think → maybe use a tool → read the result → answer. Built with LangGraph."],
  ["MCP", "Model Context Protocol. A shared standard for how the brain and the toolbox talk — like USB: any compatible brain plugs into any compatible toolbox."],
  ["Tool", "One ability the toolbox offers (save a note, search notes, search the web). Each is a small function the AI may call."],
  ["Embedding", "Turning text into a list of numbers that captures its meaning. Similar meanings give similar numbers — this powers search-by-meaning."],
  ["Vector database (Qdrant)", "A database that stores those number-lists and quickly finds the closest matches. It is the app’s memory."],
  ["Frontend (React)", "The web page you see and click — chat box, notes, sidebar. Built with React."],
  ["Backend (FastAPI)", "The Python server that connects the web page to the AI brain, tools, and database."],
  ["Citation", "A shown source. When the assistant uses a note or a web page, the app displays where the answer came from."],
  ["Session", "One saved conversation. The sidebar keeps your past chats so you can return to them."],
]));

// 3. Architecture
children.push(H("3. How the Pieces Fit Together"));
children.push(p("When you send a message, it flows from the web page down to the tools and back:"));
children.push(runs([t("Browser (React)  →  Backend (FastAPI)  →  AI Agent  →  Toolbox (MCP server)", { font: "Consolas", size: 19, bold: true })], { after: 20 }));
children.push(runs([t("                                                              ├─  Qdrant  (your notes)", { font: "Consolas", size: 19 })], { after: 20 }));
children.push(runs([t("                                                              └─  Tavily  (web search)", { font: "Consolas", size: 19 })], { after: 20 }));
children.push(runs([t("        Backend also saves every chat to a small database (SQLite) for history.", { font: "Consolas", size: 18, color: "777777" })], { after: 120 }));
children.push(p("The backend is the hub. It receives your message, runs the AI agent, streams the reply back to the page word-by-word, collects the sources the agent used, and stores the conversation. The agent reaches the actual tools through the MCP server."));

children.push(new Paragraph({ children: [new PageBreak()] }));

// 4. Features
children.push(H("4. What You Can Do (Features)"));
children.push(table([2400, 6960], [
  ["Feature", "What it does for you"],
  ["Chat assistant", "Ask in plain English. Answers stream in live. The assistant decides on its own whether to use your notes or the web."],
  ["Notes management", "Create, edit, search, and delete notes directly in a Notes screen — no chat needed."],
  ["Semantic search", "Find notes by meaning. Searching “document retrieval tips” can surface a note titled “RAG.”"],
  ["Web search", "Ask about current events or live facts; the assistant searches the internet via Tavily."],
  ["Citations", "Every answer shows clickable source chips — which note, or which web page (with link), it used."],
  ["Chat history", "Past conversations are saved in a sidebar; reopen or delete any of them."],
]));

// 5. Tools
children.push(H("5. The Tools the Assistant Can Use"));
children.push(p("Behind the scenes, the assistant has six tools it can choose from:"));
children.push(table([2200, 5160, 2000], [
  ["Tool", "What it does", "Needs"],
  ["add_note", "Saves a new note (and embeds it for search).", "Local model"],
  ["search_notes", "Finds notes closest in meaning to a query.", "Local model"],
  ["list_notes", "Lists all saved notes.", "Nothing extra"],
  ["update_note", "Edits an existing note by its id.", "Local model"],
  ["delete_note", "Removes a note by its id.", "Nothing extra"],
  ["search_web", "Searches the live internet via Tavily.", "Tavily key"],
]));
children.push(p("Saving and searching notes are completely free (embeddings run locally on your computer). Only the web search needs a free Tavily key, and the brain needs a free OpenRouter key.", { italics: true }));

// 6. Worked example
children.push(H("6. A Complete Example, Step by Step"));
children.push(p("Example A — saving and recalling a note. You type in the chat:"));
children.push(code("Save a note titled ‘Meeting’: Ship MVP by Friday"));
children.push(numbered([t("The page sends your message to the backend, which starts the AI agent.", {})]));
children.push(numbered([t("The brain reasons: “This is a save request” → it calls add_note.", {})]));
children.push(numbered([t("The toolbox turns the text into an embedding and stores it in Qdrant.", {})]));
children.push(numbered([t("The reply streams back: “Saved your note ‘Meeting’.”", {})]));
children.push(p("Later you ask, using different words:", { before: 60 }));
children.push(code("What did I plan to ship?"));
children.push(bullet("The brain calls search_notes; Qdrant returns the “Meeting” note by meaning."));
children.push(bullet("The answer streams in, and a citation chip shows the “Meeting” note as the source."));

children.push(p("Example B — a web search. You ask:", { before: 80 }));
children.push(code("Search the web: what is the latest LangGraph version?"));
children.push(bullet("The brain decides this is current info → it calls search_web (Tavily)."));
children.push(bullet("It reads the live results and replies, e.g. “The latest release is 1.2.6.”"));
children.push(bullet("Citation chips appear with clickable links to the source web pages."));
children.push(p("The assistant chooses the right tool by itself — your notes for your own content, the web for live facts.", { italics: true }));

children.push(new Paragraph({ children: [new PageBreak()] }));

// 7. Cases
children.push(H("7. What Happens in Different Situations"));
children.push(table([3200, 6160], [
  ["Situation", "What happens"],
  ["You have no notes yet", "The assistant says you have none, instead of inventing any."],
  ["You deleted notes, then ask again", "The assistant re-checks the live database every time, so it reflects the current notes (never stale chat history)."],
  ["You ask about current events", "It searches the web (Tavily) rather than your notes."],
  ["No Tavily key is set", "Web search is simply skipped with “unavailable” — notes still work fully."],
  ["The free brain model is busy", "You may see a rate-limit message; retry, or switch the model in the .env file."],
  ["Two notes are similar", "Both are returned, ranked by a similarity score (higher = closer)."],
  ["A service is not running", "Chat reports it can’t reach a service; start the missing piece (usually Docker/Qdrant)."],
]));

// 8. How to run
children.push(H("8. How to Run It"));
children.push(p("The app runs as four background pieces. The easiest way is the one-click launcher:"));
children.push(numbered([t("Double-click start_app.bat. ", { bold: true }), t("It starts Docker + the database, the toolbox, the backend, and the web page, then opens your browser.")]));
children.push(numbered([t("Use the app at ", {}), t("http://localhost:3000", { font: "Consolas", size: 20 }), t(".", {})]));
children.push(numbered([t("To stop everything, double-click stop_app.bat.", {})]));
children.push(p("The four pieces it launches:"));
children.push(table([3400, 1500, 4460], [
  ["Piece", "Port", "Role"],
  ["Qdrant (Docker)", "6333", "Stores your notes (memory)"],
  ["MCP server", "8001", "The toolbox of abilities"],
  ["Backend API", "8000", "The hub: runs the agent, streams replies"],
  ["Frontend (React)", "3000", "The web page you use"],
]));
children.push(p("One free OpenRouter key (in the .env file) is required; a free Tavily key is optional for web search.", { italics: true }));

// 9. Free stack
children.push(H("9. The “Free” Setup Used Here"));
children.push(p("Everything runs at no cost, swapping paid services for free equivalents:"));
children.push(table([2700, 3330, 3330], [
  ["Job", "Typical (paid)", "This build (free)"],
  ["Make embeddings", "OpenAI", "FastEmbed (runs on your PC, no key)"],
  ["The brain", "OpenAI / Anthropic", "OpenRouter free model"],
  ["Web search", "Paid search APIs", "Tavily free tier"],
  ["Memory store", "Hosted vector DB", "Qdrant in Docker (local)"],
  ["Chat history", "Cloud database", "SQLite file (local)"],
]));
children.push(p("Result: saving and recalling notes is fully free and even works offline; only the brain and web search use the internet, both on free tiers.", { after: 40 }));

// closing line
children.push(new Paragraph({
  spacing: { before: 240 },
  children: [new TextRun({ text: "In one sentence: you chat in a web page, a free AI brain decides which tool to use through the MCP standard, the tools read or write your meaning-searchable memory or search the web, and you get a streamed, sourced answer.", italics: true, size: 22, color: BLUE, font: FONT })],
}));

// ---------- assemble ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: BLUE, font: FONT },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bul", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 520, hanging: 260 } } } },
      ] },
      { reference: "num", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 520, hanging: 260 } } } },
      ] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Personal Knowledge Assistant — Beginner Guide      Page ", size: 18, color: "888888", font: FONT }),
          new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888", font: FONT }),
        ],
      })] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("MCP_Project_Explained.docx", buf);
  console.log("Wrote MCP_Project_Explained.docx");
});
