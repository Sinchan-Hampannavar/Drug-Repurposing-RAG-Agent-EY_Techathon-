"""
Step 2: Turn papers.json into a searchable vector index.

This is the actual "RAG" part: we convert each abstract into a vector
(a list of numbers that captures its meaning) using a free local
embedding model, then store those vectors in a FAISS index so we can
later search "which abstracts are most similar to this question?"

Usage:
    python build_index.py

Reads papers.json, writes:
    - faiss_index.bin   (the vector index itself)
    - papers_store.json (the papers, in the same order as the index,
                          so we can map a search result back to text)
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, free, runs locally — no API key needed


def build_index():
    with open("papers.json") as f:
        papers = json.load(f)

    if not papers:
        raise SystemExit("papers.json is empty — run fetch_pubmed.py first")

    print(f"Loading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [f"{p['title']}\n{p['abstract']}" for p in papers]

    print(f"Embedding {len(texts)} abstracts...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    # FAISS needs a fixed vector dimension — this reads it from the embeddings
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # simple exact nearest-neighbor search
    index.add(embeddings)

    faiss.write_index(index, "faiss_index.bin")
    with open("papers_store.json", "w") as f:
        json.dump(papers, f, indent=2)

    print(f"Built index with {index.ntotal} vectors (dimension {dimension}).")
    print("Saved faiss_index.bin and papers_store.json")


if __name__ == "__main__":
    build_index()
