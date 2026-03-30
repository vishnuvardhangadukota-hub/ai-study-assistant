import streamlit as st
import tempfile
import ollama
import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

st.set_page_config(page_title="AI Study Assistant", layout="wide")

st.title(" Chat AI 🤖  ")

# Store database
if "db" not in st.session_state:
    st.session_state.db = None

# Upload PDFs
uploaded_files = st.file_uploader("📄 Upload PDFs", type="pdf", accept_multiple_files=True)

# Process PDFs
if uploaded_files and st.session_state.db is None:

    documents = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            loader = PyPDFLoader(tmp_file.name)
            documents.extend(loader.load())

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    st.session_state.db = db
    st.success("✅ PDFs processed successfully!")

# Chat input (always visible)
query = st.text_input("💬 Ask anything (PDF or general question)")

# Chat logic
if query:

    import datetime

    # 🕒 Time question
    if "time" in query.lower():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        st.write(f"⏰ Current Time: {now}")

    else:
        answer = ""

        # STEP 1: Check if PDF exists
        if st.session_state.db is not None:

            docs = st.session_state.db.similarity_search(query, k=2)

            # STEP 2: Check relevance (IMPORTANT)
            if docs and len(docs[0].page_content) > 150:

                context = "\n\n".join([doc.page_content for doc in docs])

                # STRICT PDF PROMPT
                prompt = f"""
                Answer ONLY from the given context.
                If the answer is NOT in the context, say "NOT FOUND".

                Context:
                {context}

                Question:
                {query}
                """

                response = ollama.chat(
                    model="llama3",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response["message"]["content"]

                # STEP 3: If not found → fallback
                if "NOT FOUND" in answer:
                    response = ollama.chat(
                        model="llama3",
                        messages=[{"role": "user", "content": query}]
                    )
                    answer = response["message"]["content"]

            else:
                # No good PDF match → normal AI
                response = ollama.chat(
                    model="llama3",
                    messages=[{"role": "user", "content": query}]
                )
                answer = response["message"]["content"]

        else:
            # No PDF → normal AI
            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": query}]
            )
            answer = response["message"]["content"]

        st.write("🤖 AI Answer:")
        st.write(answer)