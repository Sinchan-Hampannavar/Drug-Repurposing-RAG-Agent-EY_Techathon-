"""
The Clinical Trials Agent — same retrieve-then-generate pattern as
rag_agent.py's LiteratureAgent, but searching ClinicalTrials.gov data
instead of PubMed abstracts. Having two agents with the same shape
(retrieve + generate_answer) is what makes the router in master_agent.py
simple: it doesn't need to know the internal details of either agent,
just that both can be asked a question and will return an answer.
"""

import json
import os
import faiss
from sentence_transformers import SentenceTransformer
from google import genai

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-3.6-flash"
TOP_K = 5


class ClinicalTrialsAgent:
    def __init__(self):
        print("Loading clinical trials index and embedding model...")
        self.index = faiss.read_index("ct_faiss_index.bin")
        with open("ct_store.json") as f:
            self.trials = json.load(f)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit(
                "GEMINI_API_KEY is not set in this terminal session. "
                "Run: $env:GEMINI_API_KEY=\"your-key\" (PowerShell) before this script."
            )
        self.client = genai.Client(api_key=api_key)

    def retrieve(self, question: str, k: int = TOP_K) -> list[dict]:
        query_vector = self.embedder.encode([question], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(query_vector, k)
        return [self.trials[i] for i in indices[0] if i != -1]

    def generate_answer(self, question: str, retrieved_trials: list[dict]) -> str:
        context = "\n\n".join(
            f"[Trial {i+1}] {t['nct_id']} — {t['title']}\n"
            f"Status: {t['status']} | Conditions: {t['conditions']}\n"
            f"{t['summary']}"
            for i, t in enumerate(retrieved_trials)
        )

        prompt = f"""You are a clinical trials research assistant. Answer the
question ONLY using the trial excerpts below. Cite trials by their
[Trial N] label. If the excerpts don't contain enough information,
say so clearly instead of guessing.

Trial excerpts:
{context}

Question: {question}
"""
        response = self.client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text

    def ask(self, question: str) -> dict:
        retrieved = self.retrieve(question)
        answer = self.generate_answer(question, retrieved)
        return {"question": question, "answer": answer, "sources": retrieved}


if __name__ == "__main__":
    agent = ClinicalTrialsAgent()
    q = input("Ask a question about the indexed clinical trials: ")
    result = agent.ask(q)
    print("\n--- ANSWER ---\n")
    print(result["answer"])
    print("\n--- SOURCES USED ---")
    for t in result["sources"]:
        print(f"- {t['nct_id']}: {t['title']} ({t['status']})")
