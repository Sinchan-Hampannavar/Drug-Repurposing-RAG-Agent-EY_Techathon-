"""
Fetch clinical trial records from ClinicalTrials.gov (API v2, free, no key needed).

Usage:
    python fetch_clinicaltrials.py "metformin cancer" --max 100

Writes clinicaltrials.json — a list of {nct_id, title, status, conditions,
summary} records, in the same spirit as papers.json from fetch_pubmed.py.
"""

import argparse
import json
import requests

API_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trials(query: str, max_results: int) -> list[dict]:
    params = {
        "query.term": query,
        "pageSize": min(max_results, 100),  # API caps page size at 100
         "fields": "NCTId,BriefTitle,OverallStatus,Condition,BriefSummary",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    trials = []
    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        description = protocol.get("descriptionModule", {})

        summary = description.get("briefSummary", "")
        if not summary:
            continue  # skip trials with no usable text to embed

        trials.append({
            "nct_id": identification.get("nctId", ""),
            "title": identification.get("briefTitle", ""),
            "status": status.get("overallStatus", ""),
            "conditions": ", ".join(conditions_module.get("conditions", [])),
            "summary": summary,
        })

    return trials


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch ClinicalTrials.gov records")
    parser.add_argument("query", help='Search query, e.g. "metformin cancer"')
    parser.add_argument("--max", type=int, default=100, help="Max trials to fetch")
    args = parser.parse_args()

    print(f"Searching ClinicalTrials.gov for: {args.query!r}")
    trials = fetch_trials(args.query, args.max)

    with open("clinicaltrials.json", "w") as f:
        json.dump(trials, f, indent=2)

    print(f"Saved {len(trials)} trials with usable summaries to clinicaltrials.json")
