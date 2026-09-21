Multi-Agent System for Drug Repurposing

A multi-agent retrieval-augmented generation (RAG) system that answers drug-repurposing questions by searching real PubMed research abstracts and real ClinicalTrials.gov trial records, routing each question to the right data source automatically, and citing exactly which sources it used.

This is a solo rebuild of a concept originally pitched at EY Techathon 6.0 (Agentic AI for pharmaceutical drug repurposing). The original hackathon demo UI was built by a teammate using Lovable; this repo is an independent, from-scratch implementation with real retrieval and generation pipelines behind it — no mocked data.

Features

Data Pipeline

Fetch PubMed Abstracts: Pulls real research papers from the PubMed API for any search query.
Fetch Clinical Trials: Pulls real trial records from the ClinicalTrials.gov API, including status, conditions, and summary.
Structured Storage: Saves both sources as clean JSON records for indexing.

Retrieval (Vector Search)

Embedding: Converts abstracts and trial summaries into vectors using a local sentence-transformer model.
Two Independent Vector Indexes: Separate FAISS indexes for literature and clinical trials, so each agent can be run standalone.
Semantic Retrieval: Finds the most relevant documents for a question, not just keyword matches.

Multi-Agent Routing

Literature Agent: Answers mechanism and evidence questions using PubMed abstracts.
Clinical Trials Agent: Answers trial status and design questions using ClinicalTrials.gov data.
Master Agent Router: Classifies each incoming question with Gemini and calls only the relevant agent(s) — literature, clinical trials, or both — before doing any retrieval.
Combined Synthesis: When both agents are needed, retrieves from both sources and generates one coherent answer that can flag conflicts between published evidence and trial outcomes.

Generation (LLM Synthesis)

Grounded Answers: Every answer is generated only from retrieved context, not from the model's general knowledge.
Source Citation: Answers cite papers as [Paper N] (with PMID) and trials as [Trial N] (with NCT ID).
Uncertainty Handling: If retrieved context doesn't support an answer, the agent says so instead of guessing.
Automatic Retry: Gemini API calls retry automatically on transient server errors instead of crashing.

Interface

Terminal Mode: Run any agent directly from the command line for quick testing.
Web UI: A Streamlit app with a search box and expandable source panels.
Tech Stack
Language: Python
Embeddings: sentence-transformers (all-MiniLM-L6-v2, runs locally)
Vector Database: faiss-cpu
LLM & Routing: Google Gemini API (google-genai)
Data Sources: PubMed API (biopython), ClinicalTrials.gov API (requests)
Frontend: streamlit
File-Based Storage

Generated data is stored locally and excluded from version control (see .gitignore):

papers.json / clinicaltrials.json – raw fetched records from each source.
faiss_index.bin / ct_faiss_index.bin – vector indexes for literature and trials respectively.
papers_store.json / ct_store.json – records aligned to each vector index, for mapping search results back to text.
Setup
bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt

Get a free Gemini API key at aistudio.google.com/apikey (no credit card required), then set it:

bash
$env:GEMINI_API_KEY="your-key-here"     # Windows PowerShell
export GEMINI_API_KEY="your-key-here"   # Mac/Linux
Usage
bash
# 1. Download real data
python fetch_pubmed.py "metformin cancer repurposing" --max 100 --email you@example.com
python fetch_clinicaltrials.py "metformin cancer" --max 100

# 2. Build both vector indexes
python build_index.py
python build_clinicaltrials_index.py

# 3. Test each agent individually
python rag_agent.py
python clinical_trials_agent.py

# 4. Run the full multi-agent router
python master_agent.py

# 5. Run the web app
streamlit run app.py

# 6. Benchmark retrieval speed at scale
python benchmark_index.py