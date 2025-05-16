import os
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

MAX_CHARS = 16000
MODEL_NAME = "gpt-4o-mini"

# Leia sua chave da API
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("⚠️ Defina OPENAI_API_KEY em .streamlit/secrets.toml ou variável de ambiente")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_pdf_text_local(caminho_arquivo: str) -> str:
    doc = fitz.open(caminho_arquivo)
    texto = "".join(page.get_text() for page in doc)
    return texto

def ask_gpt(question: str, context: str) -> str:
    system_prompt = (
        "Você é um assistente que responde com base no PDF fornecido. "
        "Se a resposta exata não estiver no texto, responda algo semelhante ou relacionado ao tema. "
        "Se não conseguir, sugira outro tópico útil para o usuário e explique o motivo."
    )

    user_prompt = f"Documento:\n{context}\n\nPergunta do usuário: {question}"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=512,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Configura a página (tem que ser a PRIMERA linha depois dos imports)
st.set_page_config(page_title="Chat com PDF (OpenAI)", layout="centered")
st.title("📄 Chat com seu PDF usando IA")

# Caminho do seu PDF padrão
PDF_PATH = "documento.pdf"

# Carrega texto do PDF no estado da sessão
if "doc_text" not in st.session_state:
    with st.spinner("Extraindo texto do PDF …"):
        st.session_state.doc_text = extract_pdf_text_local(PDF_PATH)[:MAX_CHARS]
    st.success("Texto carregado! Agora faça perguntas.")

if "doc_text" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe conversa anterior
    for role, msg in st.session_state.messages:
        if role == "user":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    # Input do usuário
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
