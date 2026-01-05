import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# 1. Configuração da Página
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("📊 Painel de Monitoramento de TACs")

# 2. Carregamento e tratamento dos dados
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

def normalizar_texto(x):
    if isinstance(x, str):
        x = x.replace('\\n', '\n')
        x = x.replace('\r\n', '\n')
        x = x.replace('\r', '\n')
        x = ' '.join(x.splitlines())
        x = ' '.join(x.split())
    return x

df_tratado = df_tratado.applymap(normalizar_texto)

# 3. Criação dos Filtros
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)
termo_busca = st.text_input("🔍 Buscar termo em todas as colunas:", "")

# 4. Lógica de Filtragem
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    clausula_tem = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    inciso_tem = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    alinea_tem = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[clausula_tem | inciso_tem | alinea_tem]

if termo_busca:
    mask = tabela_para_exibir.astype(str).apply(
        lambda x: x.str.contains(termo_busca, case=False, na=False)
    ).any(axis=1)
    tabela_para_exibir = tabela_para_exibir[mask]

# 5. Visualização dos resultados
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    colunas_index = [
        'ANO', 'DOCUMENTO', 'CLAUSULA', 'COMPROMISSO_DA_CLAUSULA',
        'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO',
        'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO', 'ALINEA',
        'COMPROMISSO_ALINEA', 'STATUS_Da_ALINEA', 'OBS_SEJUS_ALINEA'
    ]
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    # ===============================
    # CSS DA TABELA (TELA)
    # ===============================
    st.markdown("""
    <style>
    .tabela-relatorio {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        table-layout: fixed;
    }

    .tabela-relatorio th,
    .tabela-relatorio td {
        border: 1px solid #555;
        padding: 8px;
        text-align: left;
        vertical-align: top;
        word-wrap: break-word;
        white-space: normal;
    }

    .tabela-relatorio th {
        background-color: #1f2937;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===============================
    # BOTÃO DE DOWNLOAD (PDF / HTML)
    # ===============================
    estilo_html_export = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: black; background-color: white; }
        table { width: 100%; border-collapse: collapse; font-size: 10px; }
        th, td {
            border: 1px solid #444;
            padding: 8px;
            text-align: left;
            vertical-align: top;
            white-space: pre-wrap !important;
            word-wrap: break-word;
        }
        th { background-color: #f2f2f2; font-weight: bold; }
        @media print { thead { display: table-header-group; } }
    </style>
    """
    html_tabela = tabela_visual.to_html(escape=False)
    html_final = f"<html><head><meta charset='UTF-8'>{estilo_html_export}</head><body><h2>Monitoramento de TACs</h2>{html_tabela}</body></html>"

    st.download_button(
        label="📄 Gerar Arquivo para Impressão (PDF/HTML)",
        data=html_final,
        file_name="relatorio_tac.html",
        mime="text/html"
    )

    # ===============================
    # GRÁFICO
    # ===============================
    col_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_empilhada = col_status.stack()

    lista_final = [x for x in lista_empilhada if x != '' and x != 'NÃO SE APLICA']
    contagem = pd.Series(lista_final).value_counts()
    total_geral = len(lista_final)

    def fazer_rotulo(pct):
        resultado = int(round(total_geral / 100.0 * pct))
        return f"{pct:.1f}%\n({resultado} itens)"

    col_esq, col_centro, col_dir = st.columns([1, 1, 1])
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

    # ===============================
    # TABELA ESTÁTICA (HTML)
    # ===============================
    st.write("### 📋 Relatório")

    html_tabela_site = tabela_visual.to_html(
        escape=False,
        classes="tabela-relatorio"
    )

    st.markdown(html_tabela_site, unsafe_allow_html=True)
