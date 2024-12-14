from openai import OpenAI, OpenAIError
import streamlit as st
import PyPDF2

st.title("Willkommen! Ich bin dein persönlicher AI Charisma Coach")

st.write("""
Disclaimer: Dieser Chatbot wurde von Stefan Berger (Universität Groningen) programmiert. 
Deine Interaktionen mit dem Chatbot sind vollkommen anonym und werden nicht ausgelesen. 
Viel Spass beim Chatten!
""")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set default OpenAI model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Load PDF content
pdf_path = "HBR.pdf"  # File name of the uploaded PDF
pdf_content = ""

try:
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    pdf_content = "".join(page.extract_text() for page in pdf_reader.pages)
except Exception as e:
    st.error(f"Error reading the PDF file: {e}")

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Wie kann ich dir helfen, charismatischer zu werden?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Include PDF content and specify the bot's role in the assistant's context
            system_message = {
                "role": "system",
                "content": (
                    "You are an empathetic coach who wants to help people make speeches or texts more charismatic. "
                    "Importantly, you do not just suggest blabla and bullshit, but you advise people based on scientific evidence. "
                    "For that, you rely on the article by John Antonakis, which I uploaded. This article discusses ways to make a speech more charismatic, "
                    "and this is exactly what you will apply and recommend to your clients. "
                    "Thereby, you will especially focus on verbal tactics, and not so much on non-verbal tactics, as your primary goal is to make text more charismatic. "
                    "Toward the end of a conversation, you can of course also highlight that you can give additional advice on non-verbal tactics, "
                    "but again: primarily focus on verbal tactics and improving text.\n\n"
                    f"The document contains the following content:\n\n{pdf_content}"
                )
            }

            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    system_message,
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
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
