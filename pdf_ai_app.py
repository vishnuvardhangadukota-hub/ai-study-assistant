import streamlit as st
import os
from groq import Groq
import PyPDF2
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# 🔥 GET API KEY
api_key = os.getenv("GROQ_API_KEY")

# 🔥 INIT CLIENT
client = Groq(api_key=api_key) if api_key else None

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# 🔥 DEBUG (IMPORTANT)
st.sidebar.write("API STATUS:", "FOUND ✅" if api_key else "NOT FOUND ❌")

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

st.title("🚀 AI Study Assistant")
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

    answer = ""

    try:
        # ⏰ LOCAL FEATURE
        if "time" in user_input.lower():
            answer = datetime.datetime.now().strftime("⏰ %H:%M:%S")

        else:
            # 🔥 BUILD PROMPT
            if st.session_state.pdf_text:
                prompt = f"""
You are a helpful AI assistant.

Use PDF if needed, otherwise answer normally.

PDF:
{st.session_state.pdf_text[:1000]}

Question:
{user_input}
"""
            else:
                prompt = f"You are a helpful AI assistant.\nQuestion: {user_input}"

            # 🔥 API CALL
            if api_key:
                with st.spinner("⚡ Thinking..."):
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt[:900]}]
                    )
                answer = response.choices[0].message.content
            else:
                raise Exception("API not found")

    except Exception as e:
        # 🔥 FALLBACK SYSTEM
        text = user_input.lower()

        if "what is" in text:
            answer = "🤖 This is a general concept. Please try a more specific question."

        elif "who" in text:
            answer = "🤖 It refers to a person or entity. Try specifying clearly."

        elif "why" in text:
            answer = "🤖 This usually happens due to logical or system reasons."

        elif "how" in text:
            answer = "🤖 It works step-by-step based on a process."

        elif st.session_state.pdf_text:
            answer = "📄 PDF loaded, but AI not responding. Check API key."

        else:
            answer = "⚠️ AI not working. Please check API key in Streamlit Secrets."

    # Show response
    with st.chat_message("assistant"):
        st.markdown(answer)

        pdf_file = create_pdf(answer)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Answer", f, file_name="answer.pdf")

    st.session_state.messages.append({"role": "assistant", "content": answer})