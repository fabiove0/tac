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

# 3. Criação das entradas (Sidebar)
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

# 5. Visualização dos resultados
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    # --- A. PREPARAÇÃO DOS DADOS (Primeiro preparamos tudo, depois exibimos) ---
    
    # Preparação da Tabela Agrupada
    colunas_index = ['ANO', 'DOCUMENTO', 'CLAUSULA', 'COMPROMISSO_DA_CLAUSULA', 'STATUS_DA_CLAUSULA', 'OBS_SEJUS_CLAUSULA', 'INCISO', 'COMPROMISSO_INCISO', 'STATUS_DO_INCISO', 'OBS_SEJUS_INCISO']
    tabela_visual = tabela_para_exibir.set_index(colunas_index)

    # Preparação do Gráfico
    colunas_status = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_empilhada = colunas_status.stack()
    if escolha_status == 'Todos':
        lista_final = [x for x in lista_empilhada if x != '']
    else:
        lista_final = [x for x in lista_empilhada if x != '' and x == escolha_status]
    
    contagem = pd.Series(lista_final).value_counts()
    total_geral = len(lista_final)

    # Preparação do HTML para Impressão
    estilo_html = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: black; background-color: white; }
        table { width: 100%; border-collapse: collapse; font-size: 9px; color: black; }
        th { background-color: #262730; color: white; padding: 6px; text-align: left; border: 1px solid #ccc; }
        td { border: 1px solid #ccc; padding: 4px; vertical-align: top; color: black; }
        h2 { text-align: center; }
        @media print { 
            header, footer, .no-print { display: none; } 
            table { page-break-inside: auto; }
            tr { page-break-inside: avoid; page-break-after: auto; }
            thead { display: table-header-group; }
        }
    </style>
    """
    html_tabela = tabela_visual.to_html()
    html_final = f"<html><head>{estilo_html}</head><body><h2>Monitoramento de TACs</h2>{html_tabela}</body></html>"

    # --- B. EXIBIÇÃO NA INTERFACE ---

    # 1. Botões de Exportação
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📄 Gerar Arquivo para Impressão (PDF/HTML)",
            data=html_final, # Agora a variável html_final já existe!
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

    # 2. Gráfico de Pizza
    def fazer_rotulo(pct):
        resultado = int(round(total_geral / 100.0 * pct))
        return f"{pct:.1f}%\n({resultado} itens)"

    col_esq, col_centro, col_dir = st.columns([1, 1, 1])
    with col_centro:
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.pie(contagem.values, labels=contagem.index, autopct=fazer_rotulo, 
               startangle=140, colors=plt.cm.Paired.colors, textprops={'fontsize': 5})
        ax.set_title(f"Status Geral", fontsize=6)
        st.pyplot(fig, use_container_width=False)

    # 3. Tabela Visual (Com CSS para não ficar branca)
    st.markdown("""
        <style>
        div[data-testid="stTable"] table { font-size: 9px !important; color: black !important; background-color: white !important; }
        div[data-testid="stTable"] td { color: black !important; background-color: white !important; }
        div[data-testid="stTable"] th { background-color: #f0f2f6 !important; color: black !important; }
        </style>
        """, unsafe_allow_html=True)

    st.write("### Prévia dos Dados (Agrupada)")
    st.table(tabela_visual)
