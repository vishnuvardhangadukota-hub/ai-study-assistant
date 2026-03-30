import streamlit as st
import tempfile
import datetime
from groq import Groq

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# 🔑 Add your API key here
client = Groq(api_key="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")

st.set_page_config(page_title="AI Study Assistant", layout="wide")

st.title("🌐 AI Study Assistant ")

# Session state
if "db" not in st.session_state:
    st.session_state.db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔥 CACHE PDF PROCESSING
@st.cache_resource
def process_pdfs(uploaded_files):
    documents = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            loader = PyPDFLoader(tmp_file.name)
            documents.extend(loader.load())

    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    return db

# Upload PDFs
uploaded_files = st.file_uploader("📄 Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.session_state.db = process_pdfs(uploaded_files)
    st.success("✅ PDFs processed!")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("💬 Ask anything...")

if user_input:

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 🕒 Time feature
    if "time" in user_input.lower():
        answer = datetime.datetime.now().strftime("⏰ %H:%M:%S")

    else:
        answer = ""

        # PDF logic
        if st.session_state.db is not None:

            docs = st.session_state.db.similarity_search(user_input, k=1)

            if docs and len(docs[0].page_content) > 150:

                context = docs[0].page_content

                prompt = f"""
                Answer ONLY from the context.
                If not found, say NOT FOUND.

                Context:
                {context}

                Question:
                {user_input}
                """

                with st.spinner("⚡ AI thinking..."):
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt}]
                    )

                answer = response.choices[0].message.content

                # fallback
                if "NOT FOUND" in answer:
                    with st.spinner("⚡ Thinking..."):
                        response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": user_input}]
                        )
                    answer = response.choices[0].message.content

            else:
                with st.spinner("⚡ Thinking..."):
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": user_input}]
                    )
                answer = response.choices[0].message.content

        else:
            with st.spinner("⚡ Thinking..."):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": user_input}]
                )
            answer = response.choices[0].message.content

    # Show AI response
    with st.chat_message("assistant"):
        st.write(answer)

    # Save AI message
    st.session_state.messages.append({"role": "assistant", "content": answer})