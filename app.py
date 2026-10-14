import streamlit as st
import streamlit.components.v1 as components

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard Executivo de Frequência - Outubro 2026",
    page_icon="📊",
    layout="wide"
)

# Lendo o arquivo HTML gerado
html_file_path = "dashboard_de_frequ_ncia_escolar (1).html"

try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Renderizando o dashboard HTML/JS completo dentro do Streamlit com altura ideal
    components.html(html_content, height=1400, scrolling=True)

except FileNotFoundError:
    st.error(f"⚠️ O arquivo '{html_file_path}' não foi encontrado na pasta do projeto. Certifique-se de salvá-lo no mesmo diretório do app.py.")