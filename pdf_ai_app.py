import streamlit as st
import ollama
from pypdf import PdfReader

st.title("AI PDF Study Assistant 📄🤖")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

text = ""

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    for page in reader.pages:
        text += page.extract_text()

    st.success("PDF loaded successfully!")

question = st.text_input("Ask a question from the PDF")

if question:

    prompt = f"""
    Answer the question based on the following text.

    TEXT:
    {text[:3000]}

    QUESTION:
    {question}
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    st.write(response["message"]["content"])