import streamlit as st
import os
from groq import Groq

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import tempfile

# API
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

st.set_page_config(page_title="AI Study Assistant", layout="wide")
st.title("📚 AI Study Assistant")

# Session
if "db" not in st.session_state:
    st.session_state.db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        loader = PyPDFLoader(tmp.name)
        documents = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    st.session_state.db = db
    st.success("PDF processed successfully!")

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
query = st.chat_input("Ask something...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.write(query)

    try:
        if st.session_state.db:
            docs = st.session_state.db.similarity_search(query, k=1)
            context = docs[0].page_content[:500]

            prompt = f"""
Answer based on this context if relevant, else answer normally.

Context:
{context}

Question:
{query}
"""
        else:
            prompt = query

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt[:800]}]
        )

        answer = response.choices[0].message.content

    except Exception:
        answer = "⚠️ AI temporarily unavailable. Please try again."

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})