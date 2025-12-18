import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Título da Página
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("📊 Painel de Monitoramento de TACs")

# 2. Carregamento (Igual ao seu)
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

# 3. Criação dos Menus na Barra Lateral (Substitui o interact)
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos']+ sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)

# 4. Lógica de Filtro (Igual à sua função filtrar_e_mostrar)
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    clausula_tem = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    inciso_tem = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    alinea_tem = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[clausula_tem | inciso_tem | alinea_tem]

# 5. Visualização dos Resultados
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    # Preparação para o Gráfico
    colunas_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_empilhada = colunas_status.stack()

    if escolha_status == 'Todos':
        lista_final = [x for x in lista_empilhada if x != '']
    else:
        lista_final = [x for x in lista_empilhada if x != '' and x == escolha_status]

    # Criando colunas no Streamlit para colocar gráfico e tabela lado a lado
    col1, col2 = st.columns([1, 2])

    with col1:
        if len(lista_final) > 0:
            contagem = pd.Series(lista_final).value_counts()
            total_geral = len(lista_final)

            # No Streamlit, precisamos criar o objeto 'fig' para o gráfico
            fig, ax = plt.subplots()
            ax.pie(
                contagem.values,
                labels=contagem.index,
                autopct=lambda pct: f"{pct:.1f}%\n({int(round(total_geral/100.0 * pct))} itens)",
                startangle=140,
                colors=plt.cm.Paired.colors
            )
            ax.set_title(f"Status Geral")
            st.pyplot(fig) # Comando para mostrar o gráfico no site

    with col2:
        st.write("### Prévia dos Dados")
        # Mostra a tabela de forma interativa
        st.dataframe(tabela_para_exibir)
