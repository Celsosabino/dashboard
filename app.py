import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Frequência",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Frequência Escolar")
st.caption("Faça o upload da planilha diária para visualizar os dados.")

# ---------- UPLOAD ----------
arquivo = st.file_uploader(
    "📎 Envie a planilha de frequência (.xlsx)",
    type=["xlsx", "xls"]
)

if arquivo is None:
    st.info("⬆️ Envie um arquivo Excel para começar.")
    st.stop()

# ---------- LEITURA DAS ABAS ----------
try:
    xls = pd.ExcelFile(arquivo)
    abas_disponiveis = xls.sheet_names
except Exception as e:
    st.error(f"❌ Erro ao ler o arquivo: {e}")
    st.stop()

st.success(f"✅ Arquivo carregado! Abas encontradas: {', '.join(abas_disponiveis)}")

# ---------- ABA 1: FREQUÊNCIA ----------
df_freq = pd.read_excel(xls, sheet_name="Frequência")

# Remove linhas de rodapé (TOTAL, Observações, vazias, bullet points)
df_freq = df_freq[df_freq["Turma"].notna()]
df_freq = df_freq[~df_freq["Turma"].astype(str).str.contains("TOTAL|Observa", na=False)]
df_freq = df_freq[~df_freq["Turma"].astype(str).str.startswith("•", na=False)]

# Converte colunas numéricas (a planilha traz fórmulas como texto)
df_freq["Total de alunos"] = pd.to_numeric(df_freq["Total de alunos"], errors="coerce")
df_freq["Presentes"] = pd.to_numeric(df_freq["Presentes"], errors="coerce")

# Recalcula Qtd. faltosos (a planilha traz "=C2-D2" em texto)
df_freq["Qtd. faltosos"] = df_freq["Total de alunos"] - df_freq["Presentes"]

# Remove linhas onde não foi possível ler os números
df_freq = df_freq.dropna(subset=["Total de alunos", "Presentes"])

# ---------- ABA 2: FALTOSOS ----------
df_faltosos = pd.read_excel(xls, sheet_name="Faltosos")
df_faltosos = df_faltosos[df_faltosos["Turma"].notna()]
df_faltosos = df_faltosos[~df_faltosos["Turma"].astype(str).str.contains("TOTAL", na=False)]

# ---------- ABA 3: PROFESSORES AUSENTES ----------
try:
    df_prof = pd.read_excel(xls, sheet_name="Professores ausentes")
    df_prof = df_prof[df_prof["Professor(a)"].notna()]
except Exception:
    df_prof = pd.DataFrame()

# =====================================================
# KPIs GERAIS
# =====================================================
st.subheader("📌 Indicadores Gerais do Dia")

total_alunos = int(df_freq["Total de alunos"].sum())
total_presentes = int(df_freq["Presentes"].sum())
total_faltas = int(df_freq["Qtd. faltosos"].sum())
taxa_presenca = (total_presentes / total_alunos * 100) if total_alunos else 0
total_prof_ausentes = len(df_prof)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👥 Total de Alunos", total_alunos)
col2.metric("✅ Presentes", total_presentes)
col3.metric("❌ Ausentes", total_faltas)
col4.metric("📈 Taxa de Presença", f"{taxa_presenca:.1f}%")
col5.metric("🧑‍🏫 Professores Ausentes", total_prof_ausentes)

# =====================================================
# GRÁFICO: FALTAS POR TURMA
# =====================================================
st.subheader("📊 Faltas por Turma")

fig = px.bar(
    df_freq.sort_values("Qtd. faltosos", ascending=False),
    x="Turma",
    y="Qtd. faltosos",
    text="Qtd. faltosos",
    color="Qtd. faltosos",
    color_continuous_scale="Reds",
    labels={"Qtd. faltosos": "Alunos Faltosos", "Turma": "Turma"}
)
fig.update_layout(height=450, xaxis_tickangle=-45, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# =====================================================
# GRÁFICO: PRESENÇA x FALTA POR TURMA (empilhado)
# =====================================================
st.subheader("📈 Composição: Presentes x Ausentes por Turma")

df_melt = df_freq.melt(
    id_vars="Turma",
    value_vars=["Presentes", "Qtd. faltosos"],
    var_name="Situação",
    value_name="Quantidade"
)

fig2 = px.bar(
    df_melt,
    x="Turma",
    y="Quantidade",
    color="Situação",
    barmode="stack",
    color_discrete_map={"Presentes": "#2ecc71", "Qtd. faltosos": "#e74c3c"},
    labels={"Quantidade": "Alunos"}
)
fig2.update_layout(height=450, xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# TABELA: DETALHE POR TURMA
# =====================================================
st.subheader("📋 Detalhamento por Turma")

tabela = df_freq[["Turma", "Total de alunos", "Presentes", "Qtd. faltosos"]].copy()
tabela["Taxa de Presença (%)"] = (tabela["Presentes"] / tabela["Total de alunos"] * 100).round(1)
st.dataframe(tabela, use_container_width=True, hide_index=True)

# =====================================================
# LISTA DE ALUNOS FALTOSOS
# =====================================================
st.subheader("🧑‍🎓 Alunos Faltosos do Dia")

col_a, col_b = st.columns([1, 2])

with col_a:
    turmas = ["Todas"] + sorted(df_faltosos["Turma"].astype(str).unique().tolist())
    turma_filtro = st.selectbox("Filtrar por turma:", turmas)

if turma_filtro == "Todas":
    df_filtrado = df_faltosos
else:
    df_filtrado = df_faltosos[df_faltosos["Turma"].astype(str) == turma_filtro]

with col_b:
    st.write(f"**{len(df_filtrado)} aluno(s) faltoso(s)**")

st.dataframe(
    df_filtrado[["Turma", "Nome do aluno faltoso"]].sort_values("Turma"),
    use_container_width=True,
    hide_index=True
)

# =====================================================
# PROFESSORES AUSENTES
# =====================================================
if not df_prof.empty:
    st.subheader("🧑‍🏫 Professores Ausentes")
    st.dataframe(df_prof, use_container_width=True, hide_index=True)

# =====================================================
# DOWNLOAD DO RESUMO
# =====================================================
st.subheader("⬇️ Exportar Resumo")
csv = tabela.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Baixar tabela por turma (CSV)",
    data=csv,
    file_name="resumo_frequencia.csv",
    mime="text/csv"
)
