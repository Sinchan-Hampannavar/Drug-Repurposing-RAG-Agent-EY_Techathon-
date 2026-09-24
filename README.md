# 🧬 Multi-Agent System for Drug Repurposing

A **Multi-Agent Retrieval-Augmented Generation (RAG)** system that answers drug-repurposing questions by searching real **PubMed research abstracts** and **ClinicalTrials.gov trial records**, routing each question to the appropriate data source automatically, and citing exactly which sources were used.

---

## 📖 Overview

Drug repurposing—the process of finding new therapeutic uses for existing drugs—has become an important strategy for accelerating drug discovery. However, identifying promising repurposing opportunities requires researchers to manually search through large volumes of scientific literature and clinical trial records, compare evidence across multiple sources, and evaluate whether existing studies support a new indication. This process is often time-consuming, fragmented, and difficult to scale. Traditional drug discovery can take more than a decade and require billions of dollars in investment, while drug repurposing aims to shorten that timeline by leveraging existing safety and efficacy data. :contentReference[oaicite:0]{index=0}

This project addresses that challenge through a Multi-Agent Retrieval-Augmented Generation (RAG) system that automatically retrieves and analyzes information from real PubMed research abstracts and ClinicalTrials.gov trial records. Instead of manually reviewing hundreds of papers and trial reports, users can ask natural-language questions and receive evidence-backed answers within seconds.

The system uses specialized AI agents for literature analysis and clinical-trial analysis, while a master routing agent determines which source—or combination of sources—is required for a given query. Retrieved evidence is then synthesized into grounded responses with source citations, enabling faster exploration of potential drug-repurposing opportunities while maintaining transparency and traceability.

---

# ✨ Features

---

## 🔄 Data Pipeline

### 📄 Fetch PubMed Abstracts
- Pulls real research papers from the PubMed API.
- Supports custom search queries.

### 🧪 Fetch Clinical Trials
- Retrieves trial records from ClinicalTrials.gov.
- Includes status, conditions, and study summaries.

### 💾 Structured Storage
- Stores fetched records as clean JSON files.
- Ready for indexing and retrieval.

---

## 🔍 Retrieval (Vector Search)

### 🧠 Embedding Generation
- Converts abstracts and trial summaries into vectors.
- Uses local Sentence Transformer models.

### 📚 Independent Vector Indexes
- Separate FAISS indexes for:
  - Literature
  - Clinical Trials

### 🎯 Semantic Retrieval
- Finds contextually relevant documents.
- Goes beyond keyword matching.

---

## 🤖 Multi-Agent Routing

### 📑 Literature Agent
Answers:
- Drug mechanisms
- Research evidence
- Scientific findings

### 🏥 Clinical Trials Agent
Answers:
- Trial status
- Study design
- Recruitment information

### 🧭 Master Agent Router
- Classifies incoming questions using Gemini.
- Routes queries to:
  - Literature Agent
  - Clinical Trials Agent
  - Both Agents

### 🔗 Combined Synthesis
When both sources are needed:

- Retrieves evidence from both databases.
- Generates a unified response.
- Highlights conflicts between literature and trial outcomes.

---

## 📝 Generation (LLM Synthesis)

### ✅ Grounded Answers
- Generated strictly from retrieved context.
- Avoids unsupported claims.

### 📌 Source Citation
- Papers cited as **[Paper N] (PMID)**.
- Trials cited as **[Trial N] (NCT ID)**.

### ⚠️ Uncertainty Handling
- Reports insufficient evidence when appropriate.
- Avoids hallucination.

### 🔄 Automatic Retry
- Handles transient Gemini API failures gracefully.
- Prevents unexpected crashes.

---

## 💻 Interface

### 🖥️ Terminal Mode
Run agents directly from the command line.

### 🌐 Web Interface
Built with Streamlit and includes:

- Search box
- Expandable source panels
- Interactive results display

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|-----------|
| Language | Python |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Database | FAISS |
| LLM & Routing | Google Gemini API |
| Data Sources | PubMed API, ClinicalTrials.gov API |
| Frontend | Streamlit |

---

# 📂 File-Based Storage

Generated data is stored locally and excluded from version control.

### Raw Data
- `papers.json`
- `clinicaltrials.json`

### Vector Indexes
- `faiss_index.bin`
- `ct_faiss_index.bin`

### Mapping Stores
- `papers_store.json`
- `ct_store.json`

---
🔗 **Live App:** https://multiagent-system-for-drug-repurposing-ey-techathon.streamlit.app/
---

# 🚀 Setup

## 1️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure Gemini API Key

Get a free API key from:

https://aistudio.google.com/apikey

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your-key-here"
```

### Mac/Linux

```bash
export GEMINI_API_KEY="your-key-here"
```

---

# ▶️ Usage

## 1. Download Real Data

```bash
python fetch_pubmed.py "metformin cancer repurposing" --max 100 --email you@example.com

python fetch_clinicaltrials.py "metformin cancer" --max 100
```

---

## 2. Build Vector Indexes

```bash
python build_index.py

python build_clinicaltrials_index.py
```

---

## 3. Test Individual Agents

```bash
python rag_agent.py

python clinical_trials_agent.py
```

---

## 4. Run Multi-Agent Router

```bash
python master_agent.py
```

---

## 5. Launch Web Application

```bash
streamlit run app.py
```

---

## 6. Benchmark Retrieval Performance

```bash
python benchmark_index.py
```

---

# 📌 Project Highlights

✅ Real PubMed Retrieval

✅ Real ClinicalTrials.gov Retrieval

✅ Multi-Agent Architecture

✅ FAISS Semantic Search

✅ Gemini-Powered Routing

✅ Grounded Answers with Citations

✅ Streamlit Web Interface

✅ No Mock Data

---

