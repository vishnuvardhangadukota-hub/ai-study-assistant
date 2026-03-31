import streamlit as st
import os
from groq import Groq
import PyPDF2
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# API
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

st.title("🚀 AI Study Assistant (FINAL)")
st.markdown("💬 Ask anything or upload a PDF!")

# Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# Upload PDF
uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""

    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    # Limit size (important)
    st.session_state.pdf_text = text[:3000]

    st.success("✅ PDF loaded successfully!")

# Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# PDF generator
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

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        # 🔥 SMART PROMPT (THIS FIXES EVERYTHING)
        if st.session_state.pdf_text:
            prompt = f"""
You are a helpful AI assistant.

If the question is related to the PDF, use the PDF content.
If not, answer normally like ChatGPT.

PDF Content:
{st.session_state.pdf_text[:1200]}

User Question:
{user_input}
"""
        else:
            prompt = f"You are a helpful AI assistant.\nQuestion: {user_input}"

        # 🔥 CALL AI
        with st.spinner("⚡ Thinking..."):
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt[:1200]}]
            )

        answer = response.choices[0].message.content

    except Exception as e:
        # 🔥 BETTER FALLBACK
        if "time" in user_input.lower():
            answer = datetime.datetime.now().strftime("⏰ %H:%M:%S")
        elif st.session_state.pdf_text:
            answer = "📄 I couldn't process fully, but try asking a more specific question from the PDF."
        else:
            answer = "🤖 I'm having a temporary issue. Please try again."

    # Show response
    with st.chat_message("assistant"):
        st.markdown(answer)

        # Download
        pdf_file = create_pdf(answer)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Answer", f, file_name="answer.pdf")

    st.session_state.messages.append({"role": "assistant", "content": answer})