#  DocFlash AI 

> **A Source-Grounded Markdown-to-Binary Flashcard Engine.**

DocFlash AI is an end-to-end data processing pipeline that programmatically transforms unstructured, messy Markdown notes into verified, native active-recall flashcard packages (`.apkg`) ready for direct import into Anki. Built entirely in Python using Streamlit and powered by the Gemini 2.5 Flash architecture, it solves the problem of hallucination and low-context extraction by treating AI as a deterministic semantic compiler.

---

## 🚀 Core Features & Architectural Strategy

* **Deterministic Data Validation:** Bypasses unpredictable text generation strings by leveraging **Pydantic Schemas** coupled with structured JSON outputs. This guarantees the AI output mirrors exact machine-readable data slots (`front`, `back`, `card_type`, `source_quote`).
* **Structural Markdown Fragmenting:** To handle context-window limitations and eliminate the "lost-in-the-middle" problem on long texts, the backend splits inbound text along heading parameters (`#`, `##`) keeping topics contextual.
* **Source-Grounded Traceability:** Replicates the iconic NotebookLM feel. Every single card maintains an explicit connection to a verified `source_quote` from your raw note file, providing an instantly audit-capable review layout before export.
* **Rate & Budget Guardrails:** Implements strict multi-layer payload volume thresholds capping submissions to **15,000 characters (~5 pages)**. This ensures predictable token usage and blazing fast (< 30 sec) client-side response states.
* **Binary Object Compilation:** Merges individual card nodes and uses an uncompressed zip database compiler (`genanki`) to generate a true SQLite-formatted binary `.apkg` file on-the-fly.

---

##  Tech Stack & Dependencies

* **Frontend & Layout State Workspace:** Streamlit (Python)
* **AI Engine Orchestration Model:** Google GenAI SDK (`gemini-2.5-flash`)
* **Schema & Payload Validation Layer:** Pydantic v2
* **Binary Compiler Engine:** Genanki

---

##  Repository File Architecture

```text
docflash-ai/
│
├── app.py              # Main Streamlit UI layout and system session state framework
├── ai_engine.py        # Markdown text fragment splitter and structured Pydantic LLM pipelines
├── local_compiler.py   # Baseline core binary compilation script engine layer
├── .env                # Secure localized API credentials (Git-ignored)
├── .gitignore          # Production rule asset filter exclusion rules
└── requirements.txt    # Stable application dependency manifest
