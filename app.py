import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# 1. Configuração da Página
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("📊 Painel de Monitoramento de TACs")

# 2. Carregamento dos dados
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

# 3. Filtros
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)

# 4. Filtragem
tabela_para_exibir = df_tratado.copy()
if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    c = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    i = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    a = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[c | i | a]

# 5. Visualização
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado.")
else:
    # --- PASSO 1: PREPARAÇÃO DOS DADOS (Ordem correta para evitar NameError) ---
    colunas_index = [
        'ANO', 'DOCUMENTO', 'CLAUSULA', 'COMPROMISSO_DA_CLAUSULA', 
        'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 
        'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO'
    ]
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    # HTML para o arquivo baixável (Mantendo padrão para o PDF)
    estilo_html = """
    <style>
        table { width: 100%; border-collapse: collapse; font-size: 10px; color: black; background-color: white; }
        th, td { border: 1px solid #ccc; padding: 6px; text-align: left; vertical-align: top; color: black !important; background-color: white !important; }
        th { font-weight: bold; background-color: #f2f2f2 !important; }
    </style>
    """
    html_tabela = tabela_visual.to_html()
    html_final = f"<html><head><meta charset='utf-8'>{estilo_html}</head><body>{html_tabela}</body></html>"

    # --- PASSO 2: BOTÕES E GRÁFICO ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(label="📄 Gerar Arquivo para Impressão", data=html_final, file_name="relatorio.html", mime="text/html")
    with col_btn2:
        st.download_button(label="Excel: Exportar", data=tabela_para_exibir.to_csv(index=False).encode('utf-8'), file_name="dados.csv", mime="text/csv")

    # Gráfico (Fica pequeno no topo)
    col_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_final = [x for x in col_status.stack() if x != '']
    if len(lista_final) > 0:
        contagem = pd.Series(lista_final).value_counts()
        col_esq, col_centro, col_dir = st.columns([1, 1, 1])
        with col_centro:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.pie(contagem.values, labels=contagem.index, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 5})
            st.pyplot(fig, use_container_width=False)

    # --- PASSO 3: O SEGREDO DA PADRONIZAÇÃO VISUAL (CSS Unificado) ---
    st.markdown("""
        <style>
        /* Alvo: Cabeçalhos (Índice agrupado) E Células (Dados comuns) */
        div[data-testid="stTable"] th, 
        div[data-testid="stTable"] td {
            background-color: white !important; /* Força fundo branco em tudo */
            color: black !important;            /* Força texto preto em tudo */
            border: 1px solid #dee2e6 !important; /* Bordas cinza claro padrão */
            font-size: 10px !important;
            padding: 5px !important;
            vertical-align: top !important;
        }
        
        /* Opcional: Deixar o topo dos títulos um pouco diferente apenas para orientação */
        div[data-testid="stTable"] thead tr th {
            background-color: #f8f9fa !important; /* Um cinza quase branco só no topo */
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.write("### Prévia dos Dados (Agrupada)")
    st.table(tabela_visual)
