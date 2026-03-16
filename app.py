import streamlit as st
import ollama

st.set_page_config(page_title="AI Study Assistant", page_icon="🤖")

st.title("AI Study Assistant 🤖")

# chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# input box
prompt = st.chat_input("Ask your study question")

if prompt:

    # show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # AI response
    response = ollama.chat(
        model="llama3",
        messages=st.session_state.messages
    )

    answer = response["message"]["content"]

    # save response
    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)