import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# 1. Título
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("📊 Painel de Monitoramento de TACs")

# 2. Dados
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

# 3. Entradas
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos']+ sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)

# 4. Filtragem
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    clausula_tem = tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status
    inciso_tem = tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status
    alinea_tem = tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status
    tabela_para_exibir = tabela_para_exibir[clausula_tem | inciso_tem | alinea_tem]

# 5. Visualização
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    # Preparação do gráfico (Antes do set_index para não dar KeyError)
    colunas_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_empilhada = colunas_status.stack()

    if escolha_status == 'Todos':
        lista_final = [x for x in lista_empilhada if x != '']
    else:
        lista_final = [x for x in lista_empilhada if x != '' and x == escolha_status]

    # --- CORREÇÃO DE IDENTAÇÃO ---
    # Estas linhas abaixo devem estar alinhadas com o "if escolha_status" lá de cima, 
    # e não dentro do "else" dele.
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if len(lista_final) > 0:
            contagem = pd.Series(lista_final).value_counts()
            total_geral = len(lista_final)

            def fazer_rotulo(pct):
                resultado = int(round(total_geral/ 100.0 * pct))
                return f"{pct:.1f}%\n({resultado})"
            
            fig, ax = plt.subplots()
            ax.pie(contagem.values, labels=contagem.index, autopct=fazer_rotulo, startangle=140, colors=plt.cm.Paired.colors)
            ax.set_title(f"Resumo de Status")
            st.pyplot(fig)
        else:
            st.info("Sem dados para o gráfico.")

    with col2:
        st.write("### Detalhamento dos Compromissos")
        
        # Criando a tabela indexada para exibição
        tabela_visual = tabela_para_exibir.set_index(['ANO', 'DOCUMENTO','CLAUSULA'])
        
        # st.dataframe cria uma grade interativa. 
        # Para ver o efeito de "agrupamento", o índice aparece à esquerda.
        st.dataframe(tabela_visual, use_container_width=True)
