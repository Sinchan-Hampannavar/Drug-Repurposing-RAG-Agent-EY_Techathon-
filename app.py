"""
Step 4: A minimal web UI so this looks and feels like an app,
not just a terminal script.

Usage:
    streamlit run app.py

This does NOT need to be fancy — the point of this file is to prove
you can wire a real backend (rag_agent.py) to something clickable,
not to win a design award.
"""

import streamlit as st
from rag_agent import LiteratureAgent

st.set_page_config(page_title="Drug Repurposing Literature Agent", page_icon="🧬")
st.title("🧬 Drug Repurposing Literature Agent")
st.caption("RAG over PubMed abstracts — retrieval + Gemini synthesis")


@st.cache_resource
def load_agent():
    return LiteratureAgent()


agent = load_agent()

question = st.text_input(
    "Ask a question about the indexed papers",
    placeholder="e.g. Is there evidence for metformin's anti-cancer effects?",
)

if st.button("Ask") and question:
    with st.spinner("Retrieving relevant papers and generating an answer..."):
        result = agent.ask(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Sources used")
    for p in result["sources"]:
        with st.expander(f"PMID {p['pmid']} — {p['title']}"):
            st.write(p["abstract"])
