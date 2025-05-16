import streamlit as st
st.set_page_config(page_title="Chat com PDF (OpenAI)", layout="centered")

import os
import fitz  # PyMuPDF
from openai import OpenAI

# ---------- Configurações ----------
MAX_CHARS = 16000
MODEL_NAME = "gpt-4o-mini"

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("⚠️ Defina OPENAI_API_KEY em .streamlit/secrets.toml ou variável de ambiente")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    return text

def ask_gpt(question, context):
    system_prompt = (
        "Você é um assistente que responde somente com base no PDF fornecido. "
        "Se a resposta não estiver claramente presente no texto, diga educadamente que não sabe."
    )
    user_prompt = f"Documento:\n{context}\n\nPergunta do usuário: {question}"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=512,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

st.title("📄 Chat com seu PDF usando IA")

uploaded_file = st.file_uploader("1️⃣ Faça upload do seu PDF", type="pdf")

if uploaded_file and "doc_text" not in st.session_state:
    with st.spinner("Extraindo texto do PDF …"):
        st.session_state.doc_text = extract_pdf_text(uploaded_file)[:MAX_CHARS]
    st.success("Texto carregado! Agora faça perguntas.")

if "doc_text" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for role, msg in st.session_state.messages:
        if role == "user":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    user_q = st.chat_input("Digite sua pergunta sobre o PDF e pressione Enter…")
    if user_q:
        st.session_state.messages.append(("user", user_q))
        st.chat_message("user").write(user_q)

        with st.spinner("Consultando IA…"):
            answer = ask_gpt(user_q, st.session_state.doc_text)
        st.session_state.messages.append(("assistant", answer))
        st.chat_message("assistant").write(answer)

else:
    st.info("📥 Primeiro, envie um PDF para iniciar o chat.")
