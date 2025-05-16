import streamlit as st
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    st.error("⚠️ Defina a variável de ambiente OPENAI_API_KEY com sua chave da OpenAI API.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

def extrair_texto_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def resumir_texto_openai(texto, max_tokens=300):
    prompt = f"Resuma o seguinte texto de forma clara e objetiva:\n\n{texto}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

st.title("Resumidor de PDF com OpenAI GPT")

uploaded_file = st.file_uploader("Faça upload do seu arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extraindo texto do PDF..."):
        texto = extrair_texto_pdf(uploaded_file)
    if texto.strip() == "":
        st.error("Não foi possível extrair texto do PDF.")
    else:
        st.success("Texto extraído com sucesso!")
        with st.spinner("Gerando resumo com OpenAI GPT..."):
            resumo = resumir_texto_openai(texto)
        st.subheader("Resumo do documento")
        st.write(resumo)
