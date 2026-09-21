# PubMed Literature Agent (RAG)

A retrieval-augmented generation (RAG) system that searches real PubMed research abstracts and answers questions about them, citing the exact papers it used. Built to explore drug-repurposing literature, using semantic search over a vector database and an LLM for grounded synthesis.

This is a solo rebuild of one agent from a larger multi-agent concept originally pitched at EY Techathon 6.0 (Agentic AI for pharmaceutical drug repurposing). The original hackathon demo UI was built by a teammate using Lovable; this repo is an independent, from-scratch implementation of the Literature Agent with a real retrieval + generation pipeline behind it — no mocked data.

## Features

**Data Pipeline**

* Fetch Abstracts: Pulls real research papers from the PubMed API for any search query.
* Structured Storage: Saves papers as PMID, title, and abstract records in JSON.

**Retrieval (Vector Search)**

* Embedding: Converts each abstract into a vector using a local sentence-transformer model.
* Vector Index: Stores embeddings in a FAISS index for fast semantic similarity search.
* Semantic Retrieval: Finds the most relevant abstracts for a given question, not just keyword matches.

**Generation (LLM Synthesis)**

* Grounded Answers: Passes retrieved abstracts to Gemini, which answers using only that context.
* Source Citation: Every answer cites which paper(s) it drew from, by PMID.
* Uncertainty Handling: If the retrieved abstracts don't support an answer, the agent says so instead of guessing.

**Interface**

* Terminal Mode: Ask questions directly from the command line for quick testing.
* Web UI: A Streamlit app with a search box and expandable source panels for each answer.

## Tech Stack

* Language: Python
* Embeddings: `sentence-transformers` (all-MiniLM-L6-v2, runs locally)
* Vector Database: `faiss-cpu`
* LLM: Google Gemini API (`google-genai`)
* Data Source: PubMed API via `biopython`
* Frontend: `streamlit`

## File-Based Storage

Generated data is stored locally and excluded from version control (see `.gitignore`):

* `papers.json` – raw fetched abstracts from PubMed.
* `faiss_index.bin` – the vector index built from those abstracts.
* `papers_store.json` – paper records aligned to the vector index, for mapping search results back to text.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (no credit card required), then set it:

```bash
$env:GEMINI_API_KEY="your-key-here"     # Windows PowerShell
export GEMINI_API_KEY="your-key-here"   # Mac/Linux
```

## Usage

```bash
# 1. Download real papers on a topic
python fetch_pubmed.py "metformin cancer repurposing" --max 100 --email you@example.com

# 2. Build the vector index
python build_index.py

# 3. Test in the terminal
python rag_agent.py

# 4. Run the web app
streamlit run app.py
```

## Honest Limitations

* Retrieval uses exact nearest-neighbor search (`IndexFlatL2`), which works well at this scale (hundreds of papers) but would need a different FAISS index type (e.g. `IndexIVFFlat`) to scale to millions of documents.
* This is a single retrieve-then-generate loop, not a multi-step agent that can decide to search again or call other tools — a natural next extension.
* The Clinical Trial, Patent, and Market Intelligence agents from the original hackathon concept are not implemented here; this repo covers the Literature Agent only.

## Next Steps

* Add a second agent (e.g. ClinicalTrials.gov API) with a simple router that decides which agent to call per question.
* Swap `IndexFlatL2` for `IndexIVFFlat` and benchmark retrieval speed at larger scale.
* Deploy on Streamlit Community Cloud for a live demo link.
