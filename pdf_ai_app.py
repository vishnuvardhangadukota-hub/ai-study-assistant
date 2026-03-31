import streamlit as st
import tempfile
import datetime
import os
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# API KEY
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

st.title("🚀 AI Study Assistant ")
st.markdown("👋 Upload a PDF or ask anything!")

# Session state
if "db" not in st.session_state:
    st.session_state.db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Cache PDF processing
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
        st.markdown(msg["content"])

# Create PDF file
def create_pdf(text):
    file_path = "answer.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    content = [Paragraph(text, styles["Normal"])]
    doc.build(content)
    return file_path

# Chat input
user_input = st.chat_input("💬 Ask anything...")

if user_input:

    if not user_input.strip():
        st.warning("Please enter a question")
        st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Time feature
    if "time" in user_input.lower():
        answer = datetime.datetime.now().strftime("⏰ %H:%M:%S")

    else:
        answer = ""

        try:
            if st.session_state.db is not None:

                docs = st.session_state.db.similarity_search(user_input, k=1)

                if docs:
                    # 🔥 SAFE SMALL CONTEXT
                    context = docs[0].page_content[:300]

                    prompt = f"""
Answer using this context if relevant, otherwise answer normally.

Context:
{context}

Question:
{user_input}
"""
                else:
                    prompt = user_input

            else:
                prompt = user_input

            # 🔥 SINGLE SAFE API CALL
            with st.spinner("⚡ AI thinking..."):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt[:700]}]
                )

            answer = response.choices[0].message.content

        except Exception as e:
            answer = "❌ Error occurred. Please try again."

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(answer)

        # Download PDF
        pdf_file = create_pdf(answer)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Answer", f, file_name="answer.pdf")

    # Save chat
    st.session_state.messages.append({"role": "assistant", "content": answer})