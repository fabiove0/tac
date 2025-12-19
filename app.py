import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# 1. Configuração da Página (Sempre no topo)
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")

# 2. Título e CSS para diminuir a fonte da tabela
st.title("📊 Painel de Monitoramento de TACs")
st.markdown("""
    <style>
    /* Estilização para deixar a tabela compacta e legível */
    table {
        font-size: 10px !important;
        width: 100%;
    }
    th {
        background-color: #262730 !important;
        color: white !important;
    }
    td {
        border: 1px solid #4a4a4a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Carregamento dos dados
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

# 4. Filtros na Barra Lateral
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos']+ sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)

# 5. Lógica de Filtragem
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    c = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    i = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    a = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[c | i | a]

# 6. Exibição dos Resultados
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado.")
else:
    # Preparação para o Gráfico
    colunas_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_empilhada = colunas_status.stack()
    lista_final = [x for x in lista_empilhada if x != '']
    
    if escolha_status != 'Todos':
        lista_final = [x for x in lista_final if x == escolha_status]

    # --- TOPO: Gráfico Pequeno e Centralizado ---
    col_esq, col_centro, col_dir = st.columns([1, 1, 1])
    with col_centro:
        if len(lista_final) > 0:
            contagem = pd.Series(lista_final).value_counts()
            fig, ax = plt.subplots(figsize=(2, 2)) # Tamanho fixo pequeno
            ax.pie(contagem.values, labels=contagem.index, autopct='%1.1f%%', 
                   startangle=140, textprops={'fontsize': 6})
            fig.patch.set_facecolor('none') # Fundo transparente para o gráfico
            st.pyplot(fig, use_container_width=False)

    # --- BAIXO: Tabela Inteira ---
    st.write("### 📋 Relatório de Compromissos")
    
    # Criamos o agrupamento pelo índice (Ano, Doc, Cláusula)
    # Isso fará com que o st.table mescle as células iguais automaticamente
    tabela_visual = tabela_para_exibir.set_index(['ANO', 'DOCUMENTO', 'CLAUSULA'])
    
    # st.table mostra TUDO na tela sem barra de rolagem interna
    st.table(tabela_visual)
