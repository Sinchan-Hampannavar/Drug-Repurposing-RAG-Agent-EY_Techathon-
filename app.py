"""
Step 4: A minimal web UI so this looks and feels like an app,
not just a terminal script.

Usage:
    streamlit run app.py
"""

import streamlit as st
from rag_agent import LiteratureAgent

st.set_page_config(
    page_title="Drug Repurposing Literature Agent",
    page_icon="🧬",
    layout="centered",
)

st.title("🧬 Drug Repurposing Literature Agent")
st.caption("RAG over PubMed abstracts — retrieval + Gemini synthesis")

st.divider()


@st.cache_resource
def load_agent():
    return LiteratureAgent()


agent = load_agent()

# --- Example question chips -------------------------------------------------
st.markdown("**Try an example, or ask your own question:**")

examples = [
    "Is there evidence for metformin's anti-cancer effects?",
    "What is metformin's mechanism in cancer treatment?",
    "Does metformin affect tumor growth pathways?",
]

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        st.session_state.question_input = ex

question = st.text_input(
    "Ask a question about the indexed papers",
    key="question_input",
    placeholder="e.g. Is there evidence for metformin's anti-cancer effects?",
)

ask_clicked = st.button("Ask", type="primary")

# --- Run the query ------------------------------------------------------------
if ask_clicked and question:
    with st.spinner("🔍 Retrieving relevant papers and generating an answer..."):
        result = agent.ask(question)

    st.divider()

    with st.container(border=True):
        st.subheader("📋 Answer")
        st.write(result["answer"])

    st.subheader(f"📚 Sources used ({len(result['sources'])})")
    for p in result["sources"]:
        with st.expander(f"PMID {p['pmid']} — {p['title']}"):
            st.write(p["abstract"])
            st.markdown(
                f"[View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{p['pmid']}/)"
            )

elif ask_clicked and not question:
    st.warning("Type a question first, or click one of the example buttons above.")

st.divider()
st.caption(
    "Built with a FAISS vector index over locally-embedded PubMed abstracts, "
    "with Gemini used for answer synthesis and citation."
)