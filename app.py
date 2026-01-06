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

    # aplica nomes amigáveis APENAS NA EXIBIÇÃO
    tabela_visual.index.names = [
        mapa_titulos[c] for c in tabela_visual.index.names
    ]


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
                /* ======================================================
           CORES SOMENTE NAS COLUNAS DE STATUS (APP)
           ====================================================== */
        
        /* STATUS DA CLÁUSULA | INCISO | ALÍNEA */
        
        /* CONCLUÍDO */
        .tabela-relatorio tbody td:nth-child(5):contains("CONCLUÍDO"),
        .tabela-relatorio tbody td:nth-child(9):contains("CONCLUÍDO"),
        .tabela-relatorio tbody td:nth-child(13):contains("CONCLUÍDO") {
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
        }
        
        /* EM ANDAMENTO */
        .tabela-relatorio tbody td:nth-child(5):contains("EM ANDAMENTO"),
        .tabela-relatorio tbody td:nth-child(9):contains("EM ANDAMENTO"),
        .tabela-relatorio tbody td:nth-child(13):contains("EM ANDAMENTO") {
            background-color: #fff3cd;
            color: #856404;
            font-weight: bold;
        }
        
        /* NÃO INICIADO */
        .tabela-relatorio tbody td:nth-child(5):contains("NÃO INICIADO"),
        .tabela-relatorio tbody td:nth-child(9):contains("NÃO INICIADO"),
        .tabela-relatorio tbody td:nth-child(13):contains("NÃO INICIADO") {
            background-color: #f8d7da;
            color: #721c24;
            font-weight: bold;
        }
        
        /* NÃO SE APLICA */
        .tabela-relatorio tbody td:nth-child(5):contains("NÃO SE APLICA"),
        .tabela-relatorio tbody td:nth-child(9):contains("NÃO SE APLICA"),
        .tabela-relatorio tbody td:nth-child(13):contains("NÃO SE APLICA") {
            background-color: #e2e3e5;
            color: #383d41;
        }

    </style>
    """, unsafe_allow_html=True)


    # ======================================================
    # EXPORTAÇÃO HTML
    # ======================================================
    estilo_html_export = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            font-family: Arial;
            table-layout: auto;
        }

        th, td {
            border: 1px solid #444;
            padding: 8px;
            vertical-align: top;
            white-space: normal;
            word-break: keep-all;
            overflow-wrap: normal;
        }

        thead tr:first-child {
            display: none;
        }
    </style>
    """

    html_tabela = tabela_visual.to_html(
        escape=False,
        index_names=True
    )

    html_final = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            {estilo_html_export}
        </head>
        <body>
            <div style="display:flex;align-items:center;gap:15px;">
                <img src="logo_sejus.png" style="height:60px;">
                <h1>Monitoramento de TACs</h1>
            </div>
            {html_tabela}
        </body>
    </html>
    """

    st.download_button(
        "📄 Gerar Arquivo para Impressão (HTML)",
        html_final,
        "relatorio_tac.html",
        "text/html"
    )


    # ======================================================
    # GRÁFICO
    # ======================================================
    col_status = tabela_para_exibir[
        ['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']
    ]

    lista_final = [
        x for x in col_status.stack()
        if x and x != 'NÃO SE APLICA'
    ]

    contagem = pd.Series(lista_final).value_counts()
    total_geral = len(lista_final)

    _, col_centro, _ = st.columns([1, 1, 1])
    with col_centro:
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.pie(
            contagem.values,
            labels=contagem.index,
            autopct=fazer_rotulo,
            startangle=140,
            textprops={'fontsize': 6}
        )
        st.pyplot(fig)


    # ======================================================
    # TABELA FINAL (APP)
    # ======================================================
    st.write("### 📋 Relatório")

    st.markdown(
        tabela_visual.to_html(
            escape=False,
            classes="tabela-relatorio",
            index_names=True
        ),
        unsafe_allow_html=True
    )
