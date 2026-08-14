"""Streamlit web interface for United AI Agent."""

from __future__ import annotations

import streamlit as st

from core.agent import UnitedAgent
from core.providers import ProviderError


st.set_page_config(page_title="United AI Agent", page_icon="", layout="wide")


@st.cache_resource
def get_agent() -> UnitedAgent:
    return UnitedAgent()


agent = get_agent()

st.title("United AI Agent")
st.caption("Multi-provider agent with web search, file reading, Python execution, and persistent RAG memory.")

with st.sidebar:
    st.subheader("Workspace")
    st.code(agent.settings.memory_db_path, language="text")
    st.caption(f"File root: {__import__('os').getenv('AGENT_FILE_ROOT', __import__('os').getcwd())}")
    if st.button("Clear persistent memory", use_container_width=True):
        agent.clear_memory()
        st.session_state.messages = []
        st.rerun()

    st.subheader("Add knowledge")
    uploaded = st.file_uploader(
        "Upload a UTF-8 text or source file for RAG",
        type=["txt", "md", "py", "json", "csv", "yaml", "yml", "html", "css", "js", "ts"],
    )
    if uploaded is not None and st.button("Index uploaded file", use_container_width=True):
        content = uploaded.getvalue().decode("utf-8", errors="replace")
        document_id = agent.add_document(uploaded.name, content)
        st.success(f"Indexed document #{document_id}: {uploaded.name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask United anything...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = agent.chat(prompt)
            except (ProviderError, ValueError) as exc:
                answer = f"Error: {exc}"
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
