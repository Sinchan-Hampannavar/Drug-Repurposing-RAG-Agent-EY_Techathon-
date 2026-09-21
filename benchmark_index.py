"""
Benchmark: IndexFlatL2 (exact search) vs IndexIVFFlat (approximate,
clustered search) — the tradeoff mentioned in the README's limitations.

Honest note: your actual PubMed corpus is only ~100 papers, which is
too small to show a meaningful speed difference (both index types are
near-instant at that scale). To make this a genuine, defensible
benchmark, this script generates synthetic vectors at realistic scale
(same dimension as your real embeddings) to show how the two index
types behave as data grows. This is a legitimate way to benchmark
something you don't have real data for yet — just be upfront in your
README that the benchmark uses synthetic data at scale, not your real
100-paper corpus.

Usage:
    python benchmark_index.py
"""

import time
import numpy as np
import faiss

DIMENSION = 384  # matches all-MiniLM-L6-v2's output size
NUM_VECTORS = 100_000  # simulates a large literature corpus
NUM_QUERIES = 50
TOP_K = 5


def generate_synthetic_vectors(n: int, dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed=42)
    vectors = rng.random((n, dim), dtype="float32")
    return vectors


def benchmark_flat(vectors: np.ndarray, queries: np.ndarray) -> dict:
    index = faiss.IndexFlatL2(DIMENSION)

    start = time.perf_counter()
    index.add(vectors)
    build_time = time.perf_counter() - start

    start = time.perf_counter()
    for q in queries:
        index.search(q.reshape(1, -1), TOP_K)
    search_time = time.perf_counter() - start

    return {
        "build_time": build_time,
        "search_time": search_time,
        "per_query_ms": (search_time / len(queries)) * 1000,
    }


def benchmark_ivf(vectors: np.ndarray, queries: np.ndarray) -> dict:
    nlist = 100  # number of clusters — a common starting point for this scale
    quantizer = faiss.IndexFlatL2(DIMENSION)
    index = faiss.IndexIVFFlat(quantizer, DIMENSION, nlist)

    start = time.perf_counter()
    index.train(vectors)  # IVF indexes need a training step Flat doesn't
    index.add(vectors)
    build_time = time.perf_counter() - start

    index.nprobe = 10  # how many clusters to search — speed/accuracy tradeoff

    start = time.perf_counter()
    for q in queries:
        index.search(q.reshape(1, -1), TOP_K)
    search_time = time.perf_counter() - start

    return {
        "build_time": build_time,
        "search_time": search_time,
        "per_query_ms": (search_time / len(queries)) * 1000,
    }


if __name__ == "__main__":
    print(f"Generating {NUM_VECTORS:,} synthetic {DIMENSION}-dim vectors...")
    vectors = generate_synthetic_vectors(NUM_VECTORS, DIMENSION)
    queries = generate_synthetic_vectors(NUM_QUERIES, DIMENSION)

    print("\nBenchmarking IndexFlatL2 (exact search)...")
    flat_results = benchmark_flat(vectors, queries)

    print("Benchmarking IndexIVFFlat (approximate, clustered search)...")
    ivf_results = benchmark_ivf(vectors, queries)

    print("\n--- RESULTS ---")
    print(f"{'Metric':<20} {'IndexFlatL2':<15} {'IndexIVFFlat':<15}")
    print(f"{'Build time (s)':<20} {flat_results['build_time']:<15.3f} {ivf_results['build_time']:<15.3f}")
    print(f"{'Total search (s)':<20} {flat_results['search_time']:<15.4f} {ivf_results['search_time']:<15.4f}")
    print(f"{'Per query (ms)':<20} {flat_results['per_query_ms']:<15.3f} {ivf_results['per_query_ms']:<15.3f}")

    speedup = flat_results["per_query_ms"] / ivf_results["per_query_ms"]
    print(f"\nIVFFlat is approximately {speedup:.1f}x faster per query at {NUM_VECTORS:,} vectors.")
    print("(IVFFlat trades a small amount of accuracy for this speed — it searches")
    print("only the most likely clusters, not the entire dataset, unlike FlatL2.)")
