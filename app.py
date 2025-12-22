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

# 3. Filtros na Barra Lateral
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
    c = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    i = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    a = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[c | i | a]

# 5. Visualização
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado.")
else:
    # --- PASSO A: PREPARAÇÃO DOS DADOS (Necessário antes de criar os botões) ---
    colunas_index = [
        'ANO', 'DOCUMENTO', 'CLAUSULA', 'COMPROMISSO_DA_CLAUSULA', 
        'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 
        'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO'
    ]
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    # Estilo CSS para o arquivo que será baixado (PDF/HTML)
    estilo_html = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: black !important; background-color: white !important; }
        table { width: 100%; border-collapse: collapse; font-size: 10px; color: black !important; }
        th { background-color: #262730 !important; color: white !important; padding: 8px; text-align: left; border: 1px solid #ccc; }
        td { border: 1px solid #ccc; padding: 6px; vertical-align: top; color: black !important; background-color: white !important; }
        @media print { thead { display: table-header-group; } table { page-break-inside: auto; } tr { page-break-inside: avoid; } }
    </style>
    """
    html_tabela = tabela_visual.to_html()
    # AQUI DEFINIMOS A VARIÁVEL QUE ESTAVA DANDO ERRO
    html_final = f"<html><head><meta charset='utf-8'>{estilo_html}</head><body>{html_tabela}</body></html>"

    # --- PASSO B: INTERFACE (Botões e Gráfico) ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📄 Gerar Arquivo para Impressão",
            data=html_final, # Agora funciona porque html_final foi criado acima
            file_name="relatorio_tac.html",
            mime="text/html"
        )
    with col_btn2:
        st.download_button(
            label="Excel: Exportar Dados",
            data=tabela_para_exibir.to_csv(index=False).encode('utf-8'),
            file_name="dados_tac.csv",
            mime="text/csv",
        )

    # Gráfico de Pizza
    col_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_final = [x for x in col_status.stack() if x != '']
    contagem = pd.Series(lista_final).value_counts()
    
    col_esq, col_centro, col_dir = st.columns([1, 1, 1])
    with col_centro:
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.pie(contagem.values, labels=contagem.index, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 5})
        st.pyplot(fig, use_container_width=False)

    # --- PASSO C: EXIBIÇÃO DA TABELA (Forçando o padrão visual) ---
    st.markdown("""
        <style>
        /* Resolve o problema das células brancas e texto invisível no site */
        div[data-testid="stTable"] table { color: black !important; background-color: white !important; font-size: 10px; }
        div[data-testid="stTable"] td { color: black !important; background-color: white !important; border: 1px solid #ccc !important; }
        div[data-testid="stTable"] th { background-color: #262730 !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    st.write("### Prévia dos Dados (Agrupada)")
    st.table(tabela_visual)
