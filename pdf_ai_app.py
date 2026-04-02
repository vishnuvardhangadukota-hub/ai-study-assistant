import streamlit as st
import os
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile

# API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# 🌙 DARK MODE STYLE
st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    .stChatMessage {border-radius: 10px; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Study Assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

    uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

# Session state
if "db" not in st.session_state:
    st.session_state.db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Process PDF
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        loader = PyPDFLoader(tmp.name)
        docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings()
    st.session_state.db = FAISS.from_documents(docs, embeddings)

    st.success("✅ PDF Ready!")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("💬 Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        if st.session_state.db:
            docs = st.session_state.db.similarity_search(user_input, k=1)
            context = docs[0].page_content[:500]

            prompt = f"""
You are a helpful AI assistant.

Use context if relevant.

Context:
{context}

Question:
{user_input}
"""
        else:
            prompt = user_input

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt[:800]}]
        )

        answer = response.choices[0].message.content

    except Exception:
        answer = "⚠️ AI temporarily unavailable. Try again."

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})