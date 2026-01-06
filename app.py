# ==========================================================
# IMPORTAÇÕES
# ==========================================================
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("Painel de Monitoramento de TACs")


# ==========================================================
# CARREGAMENTO DOS DADOS
# ==========================================================
url = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/"
    "pub?gid=0&single=true&output=csv"
)

df = pd.read_csv(url)
df_tratado = df.fillna('')


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================
def normalizar_texto(x):
    if isinstance(x, str):
        x = x.replace('\\n', '\n')
        x = x.replace('\r\n', '\n')
        x = x.replace('\r', '\n')
        x = ' '.join(x.splitlines())
        x = ' '.join(x.split())
    return x


def fazer_rotulo(pct):
    resultado = int(round(total_geral / 100.0 * pct))
    return f"{pct:.1f}%\n({resultado} itens)"


# ==========================================================
# >>> ADIÇÃO 1 — FUNÇÃO DE COR DOS STATUS (SOMENTE APP)
# ==========================================================
def colorir_status(valor):
    if valor == "CONCLUÍDO":
        return '<span class="status-concluido">CONCLUÍDO</span>'
    if valor == "EM ANDAMENTO":
        return '<span class="status-andamento">EM ANDAMENTO</span>'
    if valor == "NÃO INICIADO":
        return '<span class="status-nao-iniciado">NÃO INICIADO</span>'
    if valor == "NÃO SE APLICA":
        return '<span class="status-nao-aplica">NÃO SE APLICA</span>'
    return valor


# ==========================================================
# TRATAMENTO DOS DADOS
# ==========================================================
df_tratado = df_tratado.applymap(normalizar_texto)


# ==========================================================
# MAPA DE NOMES AMIGÁVEIS (APENAS VISUAL)
# ==========================================================
mapa_titulos = {
    'ANO': 'Ano',
    'DOCUMENTO': 'Documento',
    'CLAUSULA': 'Cláusula',
    'COMPROMISSO_DA_CLAUSULA': 'Compromisso da Cláusula',
    'STATUS_DA_CLAUSULA': 'Status da Cláusula',
    'OBS_SEJUS_CLAUSULA': 'Observações (SEJUS) – Cláusula',
    'INCISO': 'Inciso',
    'COMPROMISSO_INCISO': 'Compromisso do Inciso',
    'STATUS_DO_INCISO': 'Status do Inciso',
    'OBS_SEJUS_INCISO': 'Observações (SEJUS) – Inciso',
    'ALINEA': 'Alínea',
    'COMPROMISSO_ALINEA': 'Compromisso da Alínea',
    'STATUS_DA_ALINEA': 'Status da Alínea',
    'OBS_SEJUS_ALINEA': 'Observações (SEJUS) – Alínea'
}


# ==========================================================
# FILTROS (SIDEBAR)
# ==========================================================
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.image("logo_sejus.png", use_container_width=True)
st.sidebar.header("Filtros")

escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)
termo_busca = st.text_input("🔍 Filtrar tabela por termo:", "")


# ==========================================================
# LÓGICA DE FILTRAGEM
# ==========================================================
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[
        tabela_para_exibir['DOCUMENTO'] == escolha_tac
    ]

if escolha_status != 'Todos':
    tabela_para_exibir = tabela_para_exibir[
        (tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status) |
        (tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status) |
        (tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status)
    ]

if termo_busca:
    mask = tabela_para_exibir.astype(str).apply(
        lambda x: x.str.contains(termo_busca, case=False, na=False)
    ).any(axis=1)
    tabela_para_exibir = tabela_para_exibir[mask]


# ==========================================================
# VISUALIZAÇÃO
# ==========================================================
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")

else:
    colunas_index = list(mapa_titulos.keys())
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    tabela_visual.index.names = [
        mapa_titulos[c] for c in tabela_visual.index.names
    ]

    # ======================================================
    # >>> ADIÇÃO 2 — CÓPIA SOMENTE PARA O APP (SEM AFETAR HTML)
    # ======================================================
    tabela_app = tabela_visual.copy()

    for col in [
        'STATUS_DA_CLAUSULA',
        'STATUS_DO_INCISO',
        'STATUS_DA_ALINEA'
    ]:
        tabela_app[col] = tabela_app[col].apply(colorir_status)


    # ======================================================
    # CSS DA TABELA (APP)
    # ======================================================
    st.markdown("""
    <style>
        .tabela-relatorio {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            table-layout: auto;
            background-color: white;
            color: black;
        }

        .tabela-relatorio th,
        .tabela-relatorio td {
            border: 1px solid #444;
            padding: 8px;
            vertical-align: top;
            white-space: normal;
            word-break: keep-all;
            overflow-wrap: normal;
        }

        .tabela-relatorio th {
            font-weight: bold;
            text-align: center;
        }

        .tabela-relatorio thead tr:first-child {
            display: none;
        }

        /* >>> ADIÇÃO 3 — CORES DOS STATUS (SOMENTE APP) */
        .status-concluido {
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
        }

        .status-andamento {
            background-color: #fff3cd;
            color: #856404;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
        }

        .status-nao-iniciado {
            background-color: #f8d7da;
            color: #721c24;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
        }

        .status-nao-aplica {
            background-color: #e2e3e5;
            color: #383d41;
            padding: 2px 4px;
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)


    # ======================================================
    # TABELA FINAL (APP)
    # ======================================================
    st.write("### 📋 Relatório")

    st.markdown(
        tabela_app.to_html(
            escape=False,
            classes="tabela-relatorio",
            index_names=True
        ),
        unsafe_allow_html=True
    )
