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

# 3. Criação dos Filtros
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)

# 4. Lógica de Filtragem
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    clausula_tem = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    inciso_tem = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    alinea_tem = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[clausula_tem | inciso_tem | alinea_tem]

# 5. Visualização dos resultados
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    # --- PASSO A: PREPARAÇÃO DA TABELA AGRUPADA ---
    colunas_index = [
        'ANO', 'DOCUMENTO', 'CLAUSULA', 'COMPROMISSO_DA_CLAUSULA', 
        'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 
        'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO'
    ]
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    # --- PASSO B: CRIAÇÃO DO ARQUIVO HTML PARA IMPRESSÃO ---
    estilo_html_export = """
    <style>
        body { font-family: Arial, sans-serif; margin: 10px; background-color: white; color: black; }
        table { width: 100%; border-collapse: collapse; font-size: 8px; color: black; table-layout: auto; }
        th, td { border: 1px solid #444; padding: 3px; text-align: left; vertical-align: top; white-space: normal; }
        /* Impede que colunas pequenas quebrem linha (ex: ANO) */
        th:nth-child(-n+3), td:nth-child(-n+3) { white-space: nowrap; }
        thead th { background-color: #f2f2f2; font-weight: bold; }
        @media print { thead { display: table-header-group; } table { page-break-inside: auto; } tr { page-break-inside: avoid; } }
    </style>
    """
    html_tabela = tabela_visual.to_html()
    html_final = f"<html><head><meta charset='UTF-8'>{estilo_html_export}</head><body>{html_tabela}</body></html>"

    # --- PASSO C: BOTÕES E GRÁFICO ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(label="📄 Gerar Arquivo para Impressão", data=html_final, file_name="relatorio.html", mime="text/html")
    with col_btn2:
        st.download_button(label="Excel: Exportar", data=df_tratado.to_csv(index=False).encode('utf-8'), file_name="dados.csv", mime="text/csv")

    # Gráfico
    col_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_final = [x for x in col_status.stack() if x != '']
    if len(lista_final) > 0:
        contagem = pd.Series(lista_final).value_counts()
        col_esq, col_centro, col_dir = st.columns([1, 1, 1])
        with col_centro:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.pie(contagem.values, labels=contagem.index, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 5})
            st.pyplot(fig, use_container_width=False)

    # --- PASSO D: CSS PARA ACABAR COM O "ESPREMIDO" NO SITE ---
    st.markdown("""
        <style>
        /* Força a tabela a ter uma largura mínima para as colunas respirarem */
        div[data-testid="stTable"] {
            overflow-x: auto !important;
        }
        div[data-testid="stTable"] table {
            width: 100% !important;
            min-width: 1200px !important; /* Ajuste este valor se quiser mais ou menos espaço lateral */
            background-color: white !important;
            color: black !important;
            font-size: 9px !important;
        }
        div[data-testid="stTable"] th, div[data-testid="stTable"] td {
            background-color: white !important;
            color: black !important;
            border: 1px solid #444 !important;
            padding: 3px 5px !important; /* Padding reduzido para ganhar espaço */
            vertical-align: top !important;
            white-space: normal !important; /* Permite quebra nos textos longos */
        }
        /* IMPEDE O ANO E DOCUMENTO DE FICAREM VERTICAIS */
        div[data-testid="stTable"] th:nth-child(-n+3), 
        div[data-testid="stTable"] td:nth-child(-n+3) {
            white-space: nowrap !important;
        }
        div[data-testid="stTable"] thead tr th {
            background-color: #f2f2f2 !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.write("### 📋 Relatório Consolidado")
    st.table(tabela_visual)
    
