import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline

def extrair_texto_pdf(uploaded_file):
    # Faltava os ":" no final das linhas que abrem blocos
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:  
        texto = ""  # inicializa texto vazio
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def resumir_texto(texto, modelo, tamanho_maximo=1000):
    # Corrigido para fatiar o texto corretamente
    partes = [texto[i:i+tamanho_maximo] for i in range(0, len(texto), tamanho_maximo)]
    resumos = [modelo(parte)[0]['summary_text'] for parte in partes]
    return " ".join(resumos)

# Configuração da página (aspas para string)
st.set_page_config(page_title="Resumidor de PDF com IA", layout="centered")
st.title("Resumidor de PDF com Inteligência Artificial")
st.write("Faça upload de um PDF e veja o resumo automático gerado por IA.")

# Input do arquivo PDF (aspas para string)
uploaded_file = st.file_uploader("Faça upload do seu arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.info("Extraindo texto do PDF...")
    texto = extrair_texto_pdf(uploaded_file)

    if len(texto.strip()) == 0:
        st.error("Não foi possível extrair texto do PDF.")
    else:
        st.success("Texto extraído com sucesso!")
        st.write("Carregando modelo de resumo...")
        modelo_resumo = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

        st.info("Gerando resumo...")
        resumo = resumir
