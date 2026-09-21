"""
The Master Agent — this is what turns two separate RAG pipelines into
an actual multi-agent system. It does one extra thing neither sub-agent
does on its own: it decides WHICH agent(s) a question needs, before
doing any retrieval.

This is a real routing decision, not a hardcoded if/else on keywords —
it asks Gemini to classify the question first, then only calls the
agent(s) that classification says are relevant. That's the core idea
behind "agentic" systems: a step that decides what to do next, rather
than a fixed pipeline that always does the same thing.

Usage:
    python master_agent.py
"""

from google import genai
from rag_agent import LiteratureAgent
from clinical_trials_agent import ClinicalTrialsAgent
import os

GEMINI_MODEL = "gemini-3.6-flash"

ROUTING_PROMPT = """You are a routing classifier for a drug-repurposing
research assistant. Given a question, decide which data source(s) are
needed to answer it well:

- "literature" — questions about mechanisms, biological evidence,
  published research findings (e.g. "how does X affect Y")
- "clinical_trials" — questions about ongoing/completed trials, trial
  status, trial design (e.g. "is there a trial testing X for Y")
- "both" — questions that need both published evidence AND trial status

Respond with EXACTLY ONE WORD: literature, clinical_trials, or both.
No explanation, no punctuation.

Question: {question}
"""


class MasterAgent:
    def __init__(self):
        # Both sub-agents load their own index/model at startup.
        # This is slower to start but keeps each agent independent —
        # you could run either one standalone, which is good design.
        self.literature_agent = LiteratureAgent()
        self.clinical_agent = ClinicalTrialsAgent()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit(
                "GEMINI_API_KEY is not set in this terminal session. "
                "Run: $env:GEMINI_API_KEY=\"your-key\" (PowerShell) before this script."
            )
        self.router_client = genai.Client(api_key=api_key)

    def route(self, question: str) -> str:
        """Ask Gemini which agent(s) this question needs."""
        prompt = ROUTING_PROMPT.format(question=question)
        response = self.router_client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt
        )
        decision = response.text.strip().lower()

        # Guard against the model returning something unexpected —
        # default to "both" so we never silently under-answer.
        if decision not in ("literature", "clinical_trials", "both"):
            decision = "both"
        return decision

    def ask(self, question: str) -> dict:
        decision = self.route(question)
        print(f"[Router decided: {decision}]")

        if decision == "literature":
            return {**self.literature_agent.ask(question), "agents_used": ["literature"]}

        if decision == "clinical_trials":
            return {**self.clinical_agent.ask(question), "agents_used": ["clinical_trials"]}

        # decision == "both": retrieve from each, then do ONE combined
        # generation call so the final answer is coherent rather than
        # two separate answers stapled together.
        lit_sources = self.literature_agent.retrieve(question)
        trial_sources = self.clinical_agent.retrieve(question)

        lit_context = "\n\n".join(
            f"[Paper {i+1}] PMID {p['pmid']} — {p['title']}\n{p['abstract']}"
            for i, p in enumerate(lit_sources)
        )
        trial_context = "\n\n".join(
            f"[Trial {i+1}] {t['nct_id']} — {t['title']} ({t['status']})\n{t['summary']}"
            for i, t in enumerate(trial_sources)
        )

        combined_prompt = f"""You are a drug-repurposing research assistant.
Answer the question using BOTH the published research excerpts and the
clinical trial excerpts below. Cite papers as [Paper N] and trials as
[Trial N]. If information conflicts between sources, point that out.

Published research:
{lit_context}

Clinical trials:
{trial_context}

Question: {question}
"""
        response = self.literature_agent.client.models.generate_content(
            model=GEMINI_MODEL, contents=combined_prompt
        )

        return {
            "question": question,
            "answer": response.text,
            "sources": {"literature": lit_sources, "clinical_trials": trial_sources},
            "agents_used": ["literature", "clinical_trials"],
        }


if __name__ == "__main__":
    master = MasterAgent()
    q = input("Ask a drug-repurposing question: ")
    result = master.ask(q)
    print(f"\n--- ANSWER (used: {', '.join(result['agents_used'])}) ---\n")
    print(result["answer"])
