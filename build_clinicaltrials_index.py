"""
Build a searchable vector index from clinicaltrials.json.
Same idea as build_index.py, just pointed at trial summaries instead
of PubMed abstracts, and writing to separate files so the two agents
don't overwrite each other's data.

Usage:
    python build_clinicaltrials_index.py
"""

import json
import faiss
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def build_index():
    with open("clinicaltrials.json") as f:
        trials = json.load(f)

    if not trials:
        raise SystemExit("clinicaltrials.json is empty — run fetch_clinicaltrials.py first")

    print(f"Loading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [f"{t['title']}\n{t['conditions']}\n{t['summary']}" for t in trials]

    print(f"Embedding {len(texts)} trial summaries...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, "ct_faiss_index.bin")
    with open("ct_store.json", "w") as f:
        json.dump(trials, f, indent=2)

    print(f"Built clinical trials index with {index.ntotal} vectors (dimension {dimension}).")
    print("Saved ct_faiss_index.bin and ct_store.json")


if __name__ == "__main__":
    build_index()
