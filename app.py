import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# 1. Título da Página
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("📊 Painel de Monitoramento de TACs")

# 2. Carregameno e tratamento dos dados
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/pub?gid=0&single=true&output=csv'
df = pd.read_csv(url)
df_tratado = df.fillna('')

#  3. Criação das entradas

#reunindo opções de alternantes
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos']+ sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

#recebimento de entradas
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

# vizualização dos resultados
if len(tabela_para_exibir) == 0:
  st.warning("Nenhum dado encontrado com esse filtro.")
else:
  # preparação do gráfico:
  colunas_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
  lista_empilhada = colunas_status.stack()

  if escolha_status == 'Todos':
    lista_final = [x for x in lista_empilhada if x != '']
  else:
    lista_final = [x for x in lista_empilhada if x != '' and x == escolha_status]


  contagem = pd.Series(lista_final).value_counts()
  total_geral = len(lista_final)

  # Desenha a Pizza
  def fazer_rotulo (pct):
    resultado= int(round(total_geral/ 100.0 * pct))
    return f"{pct:.1f}%\n({resultado} itens)"
  # Criamos 3 colunas: as das pontas vazias servem apenas para "empurrar" a do meio
  col_esq, col_centro, col_dir = st.columns([1, 1, 1]) 
  
  with col_centro:
    fig, ax = plt.subplots(figsize=(3, 3))                      # 1. Cria a base
    ax.pie(
        contagem.values,             # Os números
        labels=contagem.index,       # As legendas (Concluído, etc)
        autopct=fazer_rotulo,        # A porcentagem escrita
        startangle=140,              # Gira a pizza
        colors=plt.cm.Paired.colors, # Uma paleta de cores
        textprops={'fontsize': 5}    # <--- ADICIONE ESTA LINHA (tente 8, 7 ou 6)
    )
    # Título Dinâmico (Muda conforme o filtro)
    ax.set_title(f"Status Geral - Filtro: {escolha_tac}")
    st.pyplot(fig, use_container_width=False)                                 # 3. Entrega pro Streamlit

    # Injeta CSS para diminuir a fonte da tabela
    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            font-size: 11px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # organização da tabela:
    tabela_visual = *abela_para_exibir.set_index(['ANO', 'DOCUMENTO','CLAUSULA','COMPROMISSO_DA_CLAUSULA', 'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO'  ])
    st.dataframe(
        tabela_visual,
        use_container_width=True,  # Ocupa toda a largura da tela
        height=None,               # MOSTRA A TABELA INTEIRA (sem barra de rolagem vertical)
        column_config={
                "ANO": st.column_config.TextColumn("Ano", width="small"),
                "DOCUMENTO": st.column_config.TextColumn("Tac", width="small"),
                "CLAUSULA": st.column_config.TextColumn("Cláusula", width="medium"),
                "COMPROMISSO_DA_CLAUSULA": st.column_config.TextColumn("Compromisso (Cláusula)", width="large"),
                "STATUS_DA_CLAUSULA": st.column_config.TextColumn("Status (Cláusula)", width="small"),
                "OBS_SEJUS_CLAUSULA": st.column_config.TextColumn("Obs. SEJUS (Cláusula)", width="medium"),
                "INCISO": st.column_config.TextColumn("Inciso", width="medium"),
                "COMPROMISSO_INCISO": st.column_config.TextColumn("Compromisso (Inciso)", width="large"),
                "STATUS_DO_INCISO": st.column_config.TextColumn("Status (Inciso)", width="small"),
                "OBS_SEJUS_INCISO": st.column_config.TextColumn("Obs. SEJUS (Inciso)", width="medium"),
                "ALINEA": st.column_config.TextColumn("Alínea", width="medium"),
                "COMPROMISSO_DA_ALINEA": st.column_config.TextColumn("Compromisso (Alínea)", width="large"),
                "STATUS_DA_ALINEA": st.column_config.TextColumn("Status (Alínea)", width="small"),
                "OBS_SEJUS_ALINEA": st.column_config.TextColumn("Obs. SEJUS (Alínea)", width="medium"),
            }
    )
  
    st.write("### Prévia dos Dados")
    # Mostra a tabela de forma interativa
    st.table(tabela_visual)
