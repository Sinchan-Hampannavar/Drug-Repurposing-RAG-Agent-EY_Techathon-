"""
Step 3: The actual RAG + agent logic.

This is the core "engineering" piece — everything else is plumbing
around this file. It does two things:

  1. RETRIEVE: given a question, find the most relevant abstracts
     in our FAISS index (this is the "R" in RAG).
  2. GENERATE: hand those abstracts + the question to an LLM (Claude)
     and ask it to synthesize a grounded answer, citing which papers
     it used (this is the "AG" in RAG).

This single retrieve-then-generate loop IS a legitimate RAG agent.
You can later extend it into a multi-step "agent" by letting the LLM
decide whether to retrieve again, call other tools, etc. — but this
is the real foundation, not a toy version of it.

Uses Google's Gemini API, which has a genuinely free tier (no credit
card required). Get a key at https://aistudio.google.com/apikey and
set it as an environment variable:
    export GEMINI_API_KEY="your-key-here"
"""

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-3.6-flash"
TOP_K = 5  # how many abstracts to retrieve per question


class LiteratureAgent:
    def __init__(self):
        print("Loading index and embedding model...")
        self.index = faiss.read_index("faiss_index.bin")
        with open("papers_store.json") as f:
            self.papers = json.load(f)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.client = genai.Client()  # reads GEMINI_API_KEY from env

    def retrieve(self, question: str, k: int = TOP_K) -> list[dict]:
        """Find the k most relevant abstracts for a question."""
        query_vector = self.embedder.encode([question], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(query_vector, k)
        results = [self.papers[i] for i in indices[0] if i != -1]
        return results

    def generate_answer(self, question: str, retrieved_papers: list[dict]) -> str:
        """Ask Gemini to synthesize an answer grounded in the retrieved abstracts."""
        context = "\n\n".join(
            f"[Paper {i+1}] PMID {p['pmid']} — {p['title']}\n{p['abstract']}"
            for i, p in enumerate(retrieved_papers)
        )

        prompt = f"""You are a drug-repurposing research assistant. Answer the
question ONLY using the paper excerpts below. Cite papers by their
[Paper N] label. If the excerpts don't contain enough information,
say so clearly instead of guessing.

Paper excerpts:
{context}

Question: {question}
"""

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text

    def ask(self, question: str) -> dict:
        """The full agent loop: retrieve, then generate."""
        retrieved = self.retrieve(question)
        answer = self.generate_answer(question, retrieved)
        return {"question": question, "answer": answer, "sources": retrieved}


if __name__ == "__main__":
    agent = LiteratureAgent()
    q = input("Ask a question about the indexed papers: ")
    result = agent.ask(q)
    print("\n--- ANSWER ---\n")
    print(result["answer"])
    print("\n--- SOURCES USED ---")
    for p in result["sources"]:
        print(f"- PMID {p['pmid']}: {p['title']}")
