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
  # 2. CRIANDO O ARQUIVO DE IMPRESSÃO (HTML)
    # Criamos um estilo CSS para o arquivo que será baixado
  estilo_html = """
  <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      table { width: 100%; border-collapse: collapse; font-size: 10px; }
      th { background-color: #262730; color: white; padding: 8px; text-align: left; }
      td { border: 1px solid #ccc; padding: 6px; vertical-align: top; }
      h2 { text-align: center; color: #333; }
      @media print {
          header, footer { display: none; }
          table { page-break-inside: auto; }
          tr { page-break-inside: avoid; page-break-after: auto; }
          thead { display: table-header-group; }
      }
  </style>
  """
  

  # 3. BOTÕES NA INTERFACE DO STREAMLIT
  col_btn1, col_btn2 = st.columns(2)
  
  with col_btn1:
      # Botão para baixar a versão de impressão
      st.download_button(
          label="📄 Gerar Arquivo para Impressão (PDF/HTML)",
          data=html_final,
          file_name="relatorio_tac.html",
          mime="text/html",
          help="Baixe este arquivo, abra-o e aperte Ctrl+P para salvar como PDF"
      )
  
  with col_btn2:
      # Botão para Excel (Sempre bom ter como backup para 14 colunas)
      # Requer a biblioteca 'openpyxl' instalada
      st.download_button(
          label="Excel: Exportar Dados",
          data=tabela_para_exibir.to_csv(index=False).encode('utf-8'),
          file_name="dados_tac.csv",
          mime="text/csv",
      )

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
    fig, ax = plt.subplots(figsize=(2, 2))                      # 1. Cria a base
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

  # 1. CSS REFORÇADO (Para evitar o problema do "tudo branco")

    
      # organização da tabela:
  tabela_visual = tabela_para_exibir.set_index(['ANO', 'DOCUMENTO','CLAUSULA','COMPROMISSO_DA_CLAUSULA', 'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO'  ])
    # Geramos o HTML da tabela usando o Pandas
  html_tabela = tabela_visual.to_html(classes='tabela_relatorio')
  html_final = f"<html><head>{estilo_html}</head><body><h2>Relatório de Monitoramento de TACs</h2>{html_tabela}</body></html>"
    
  st.write("### Prévia dos Dados")
    # Mostra a tabela de forma interativa
  st.table(tabela_visual)
