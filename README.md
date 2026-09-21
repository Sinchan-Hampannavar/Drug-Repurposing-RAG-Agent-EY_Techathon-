# Drug Repurposing Literature Agent — RAG Starter

A real, working retrieval-augmented generation (RAG) agent that searches
PubMed abstracts and answers questions about them, grounded in the actual
papers it retrieves and citing which one it used.

This is a solo, from-scratch rebuild inspired by the "Warriors" team's
EY Techathon 6.0 submission (Agentic AI for pharmaceutical drug
repurposing). That version's demo UI was built with Lovable by a
teammate; this repo is an independent implementation of one real agent
(the Literature Agent) with an actual retrieval + generation pipeline
behind it — no mocked data.

**Scope note:** this implements one agent (literature search), not the
full 5-agent hub-and-spoke system from the original pitch. Clinical
Trial / Patent / Market agents are future work — see the bottom of this
file.

## What you're building, in plain English

1. Download real research abstracts from PubMed on a topic.
2. Convert each abstract into a vector (numbers that capture its meaning).
3. Store those vectors so you can search "which papers are most relevant
   to this question?" — this is called a **vector database**.
4. When someone asks a question, retrieve the most relevant abstracts,
   then ask an LLM (Claude) to answer using only those abstracts,
   citing its sources. That retrieve-then-generate loop is called **RAG**.

## What to install (do this once)

1. **Python 3.10 or newer.** Check if you have it: open a terminal and run
   `python3 --version`. If you don't have it, download from
   [python.org/downloads](https://www.python.org/downloads/).
2. **A code editor.** [VS Code](https://code.visualstudio.com/) is the
   standard choice — free, install it, open this folder in it.
3. **A free Gemini API key** (no credit card required). Go to
   [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in
   with a Google account, click "Create API key," and copy it somewhere safe.

## Setup (do this once per machine)

Open a terminal **inside this project folder** and run:

```bash
# Create an isolated Python environment so packages don't clash with other projects
python3 -m venv venv

# Activate it (do this every time you open a new terminal for this project)
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install all required packages
pip install -r requirements.txt

# Set your API key for this terminal session
export GEMINI_API_KEY="your-key-here"          # Mac/Linux
$env:GEMINI_API_KEY="your-key-here"            # Windows PowerShell
set GEMINI_API_KEY=your-key-here               # Windows Command Prompt
```

## Running it, step by step

**Step 1 — Download papers.** Pick a real drug-repurposing topic:

```bash
python fetch_pubmed.py "metformin cancer repurposing" --max 100 --email your.email@example.com
```

This creates `papers.json`. Try a few different queries and see how
many results you get — that's a genuine judgment call you'll be able
to talk about ("I chose this query because...").

**Step 2 — Build the vector index:**

```bash
python build_index.py
```

This creates `faiss_index.bin` and `papers_store.json`. The first run
will download a small embedding model (~90MB) automatically — that's
normal, it only happens once.

**Step 3 — Try it from the terminal first:**

```bash
python rag_agent.py
```

It'll ask you a question, retrieve relevant abstracts, and print
Claude's answer plus which PMIDs it used. Get this working before
moving to the web UI — it's easier to debug here.

**Step 4 — Run the actual web app:**

```bash
streamlit run app.py
```

This opens a browser tab with a simple search box. Ask questions like
"What repurposing evidence exists for this drug in oncology?"

## What to put in your GitHub repo

- All the files here
- This README, edited with what you *actually* found (which query you
  used, how many papers you indexed, example questions it answered
  well or poorly)
- A `.gitignore` that excludes `venv/`, `papers.json`, `faiss_index.bin`,
  and `papers_store.json` (these are generated, not source code —
  regenerable by anyone who runs your scripts)
- **Never commit your API key.** Don't paste it into any file that gets
  pushed to GitHub.

## Honest limitations (put these in your README too — this is a strength, not a weakness)

- Retrieval is exact nearest-neighbor search (`IndexFlatL2`), which is
  fine at this scale (hundreds of papers) but doesn't scale to millions
  without a different FAISS index type (e.g. `IndexIVFFlat`) — worth
  mentioning if asked about scale.
- This is a single retrieve-then-generate loop, not a multi-step agent
  that can decide to search again or call other tools. That's the
  natural next thing to add if you want to go further.
- Clinical Trial, Patent, and Market Intelligence agents from the
  original hackathon concept are not implemented here.

## Natural next steps (optional, if you want to go further)

- Add a second agent (e.g. ClinicalTrials.gov API) and a simple
  "Master Agent" that decides which sub-agent(s) to call based on the
  question — this is what turns a RAG pipeline into a genuine
  multi-agent system.
- Swap `IndexFlatL2` for `IndexIVFFlat` and measure the speed difference
  — a good talking point about retrieval at scale.
- Deploy it (Streamlit Community Cloud is free) so you can link a live
  demo, not just a repo.
