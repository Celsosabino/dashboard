import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
st.set_page_config(
    page_title="Dashboard de Frequência",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Executivo de Frequência")
st.caption("Faça o upload da planilha diária para visualizar os dados.")

# ---------- UPLOAD DO ARQUIVO ----------
arquivo = st.file_uploader(
    "📎 Envie a planilha de frequência (.xlsx)",
    type=["xlsx", "xls"]
)

if arquivo is None:
    st.info("⬆️ Envie um arquivo Excel para começar.")
    st.stop()  # Para a execução aqui até o usuário subir o arquivo

# ---------- LEITURA DOS DADOS ----------
try:
    df = pd.read_excel(arquivo)
except Exception as e:
    st.error(f"❌ Erro ao ler o arquivo: {e}")
    st.stop()

# Normaliza nomes das colunas (remove espaços extras)
df.columns = df.columns.str.strip()

st.success(f"✅ Planilha carregada com sucesso! ({len(df)} registros)")

# ---------- PRÉVIA DOS DADOS ----------
with st.expander("🔍 Ver dados brutos"):
    st.dataframe(df, use_container_width=True)

# ---------- KPIs (ajuste os nomes das colunas conforme seu Excel) ----------
st.subheader("📌 Indicadores Gerais")

col1, col2, col3 = st.columns(3)

# ⚠️ TROQUE os nomes 'Aluno' e 'Faltas' pelos nomes reais das suas colunas
if "Aluno" in df.columns and "Faltas" in df.columns:
    total_alunos = df["Aluno"].nunique()
    total_faltas = df["Faltas"].sum()
    media_faltas = df["Faltas"].mean()

    col1.metric("👥 Total de Alunos", total_alunos)
    col2.metric("❌ Total de Faltas", int(total_faltas))
    col3.metric("📉 Média de Faltas", f"{media_faltas:.2f}")
else:
    st.warning("⚠️ Ajuste os nomes das colunas no código (procure por 'Aluno' e 'Faltas').")

# ---------- GRÁFICO DE BARRAS ----------
if "Aluno" in df.columns and "Faltas" in df.columns:
    st.subheader("📊 Faltas por Aluno")
    
    df_agrupado = df.groupby("Aluno", as_index=False)["Faltas"].sum()
    df_agrupado = df_agrupado.sort_values("Faltas", ascending=False)

    fig = px.bar(
        df_agrupado,
        x="Aluno",
        y="Faltas",
        text="Faltas",
        color="Faltas",
        color_continuous_scale="Reds"
    )
    fig.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TABELA RESUMO ----------
if "Aluno" in df.columns and "Faltas" in df.columns:
    st.subheader("📋 Resumo por Aluno")
    resumo = df.groupby("Aluno", as_index=False).agg(
        Total_Faltas=("Faltas", "sum"),
        Registros=("Faltas", "count")
    ).sort_values("Total_Faltas", ascending=False)
    st.dataframe(resumo, use_container_width=True)
