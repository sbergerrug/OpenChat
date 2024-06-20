from openai import OpenAI, OpenAIError
import streamlit as st

st.title("Willkommen bei Charisma GPT")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Wie kann ich dir mit deiner Ansprache helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = ""
            message_placeholder = st.empty()
            for chunk in stream:
                if hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content is not None:
                        response += chunk_content
                        message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except OpenAIError as e:
            st.error(f"An error occurred: {str(e)}")
