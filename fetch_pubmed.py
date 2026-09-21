"""
Step 1: Pull abstracts from PubMed for a given query.

Usage:
    python fetch_pubmed.py "metformin cancer repurposing" --max 100

This writes a file called papers.json with a list of
{pmid, title, abstract} records, which the next script (build_index.py)
will turn into a searchable vector index.

PubMed's API is free and needs no API key, but it does ask you to
identify yourself with an email address (Entrez.email below) — this
is a courtesy/rate-limit thing, not a real credential.
"""

import argparse
import json
from Bio import Entrez, Medline


def fetch_abstracts(query: str, max_results: int, email: str) -> list[dict]:
    Entrez.email = email

    # 1. Search PubMed for matching paper IDs
    search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    search_results = Entrez.read(search_handle)
    search_handle.close()
    pmids = search_results["IdList"]

    if not pmids:
        print(f"No results found for query: {query!r}")
        return []

    print(f"Found {len(pmids)} papers. Downloading abstracts...")

    # 2. Fetch full records (title + abstract) for those IDs
    fetch_handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="text")
    records = Medline.parse(fetch_handle)

    papers = []
    for record in records:
        abstract = record.get("AB")  # AB = Abstract field in MEDLINE format
        title = record.get("TI", "")
        pmid = record.get("PMID", "")
        if abstract:  # skip papers with no abstract text
            papers.append({"pmid": pmid, "title": title, "abstract": abstract})
    fetch_handle.close()

    print(f"Kept {len(papers)} papers with usable abstracts.")
    return papers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PubMed abstracts for a query")
    parser.add_argument("query", help='Search query, e.g. "metformin cancer repurposing"')
    parser.add_argument("--max", type=int, default=100, help="Max number of papers to fetch")
    parser.add_argument(
        "--email",
        default="your.email@example.com",
        help="Your email (required by NCBI's usage policy, not verified)",
    )
    args = parser.parse_args()

    papers = fetch_abstracts(args.query, args.max, args.email)

    with open("papers.json", "w") as f:
        json.dump(papers, f, indent=2)

    print(f"Saved {len(papers)} papers to papers.json")
