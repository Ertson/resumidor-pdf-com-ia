import os
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# ---------- Configurações ---------------------------------------------
MAX_CHARS = 16000  # limite para texto extraído do PDF
MODEL_NAME = "gpt-4o-mini"  # modelo OpenAI (pode mudar)

PDF_PATH = "documento.pdf"  # arquivo PDF fixo que vai ler

# Leia a chave da OpenAI da variável ambiente ou do secrets.toml
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("⚠️ Defina a variável OPENAI_API_KEY no .streamlit/secrets.toml ou nas variáveis de ambiente")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- Funções -----------------------------------------------------

def extract_pdf_text_local(caminho_arquivo: str) -> str:
    """Extrai texto completo do PDF local"""
    doc = fitz.open(caminho_arquivo)
    text = "".join(page.get_text() for page in doc)
    return text

def ask_gpt(question: str, context: str) -> str:
    """Envia pergunta com contexto do PDF para OpenAI e recebe resposta"""
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

# ---------- Interface ---------------------------------------------------

st.set_page_config(page_title="Chat com PDF padrão (OpenAI)", layout="centered")
st.title("📄 Chat com PDF fixo usando IA")

if "doc_text" not in st.session_state:
    with st.spinner(f"Carregando texto do PDF '{PDF_PATH}'..."):
        st.session_state.doc_text = extract_pdf_text_local(PDF_PATH)[:MAX_CHARS]
    st.success("Texto carregado! Agora faça perguntas.")

if "doc_text" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []  # lista de (role, content)

    # Mostrar conversa anterior
    for role, msg in st.session_state.messages:
        if role == "user":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    # Campo para o usuário digitar a pergunta
    user_q = st.chat_input("Digite sua pergunta sobre o PDF e pressione Enter…")
    if user_q:
        st.session_state.messages.append(("user", user_q))
        st.chat_message("user").write(user_q)

        with st.spinner("Consultando IA…"):
            answer = ask_gpt(user_q, st.session_state.doc_text)
        st.session_state.messages.append(("assistant", answer))
        /app.py
/documento.pdf
