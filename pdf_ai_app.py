import streamlit as st
import os
from openai import OpenAI
import PyPDF2
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Study Assistant", layout="wide")

st.title("🚀 AI Study Assistant (FINAL WORKING)")
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
    st.success("✅ PDF loaded!")

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

# Chat
user_input = st.chat_input("💬 Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        if "time" in user_input.lower():
            answer = datetime.datetime.now().strftime("⏰ %H:%M:%S")
        else:
            if st.session_state.pdf_text:
                prompt = f"""
Use PDF if relevant, otherwise answer normally.

PDF:
{st.session_state.pdf_text[:1000]}

Question:
{user_input}
"""
            else:
                prompt = user_input

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.choices[0].message.content

    except Exception as e:
        answer = "⚠️ Something went wrong, but your app is working!"

    with st.chat_message("assistant"):
        st.markdown(answer)

        pdf_file = create_pdf(answer)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Answer", f, file_name="answer.pdf")

    st.session_state.messages.append({"role": "assistant", "content": answer})