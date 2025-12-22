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
        body { font-family: Arial, sans-serif; margin: 20px; background-color: white !important; color: black !important; }
        table { width: 100%; border-collapse: collapse; font-size: 10px; color: black !important; }
        th, td { border: 1px solid #444 !important; padding: 6px; text-align: left; vertical-align: top; color: black !important; background-color: white !important; font-weight: normal; }
        thead th { background-color: #f2f2f2 !important; font-weight: bold !important; }
        h2 { text-align: center; }
        @media print { thead { display: table-header-group; } table { page-break-inside: auto; } tr { page-break-inside: avoid; } }
    </style>
    """
    html_tabela = tabela_visual.to_html()
    html_final = f"<html><head><meta charset='UTF-8'>{estilo_html_export}</head><body><h2>Monitoramento de TACs</h2>{html_tabela}</body></html>"

    # --- PASSO C: BOTÕES E GRÁFICO ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📄 Gerar Arquivo para Impressão (PDF/HTML)",
            data=html_final,
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
    lista_empilhada = col_status.stack()
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

    # --- PASSO D: PADRONIZAÇÃO VISUAL DA TABELA NO SITE ---
    st.markdown("""
        <style>
        /* Remove qualquer barra de rolagem horizontal */
        div[data-testid="stTable"] {
            overflow-x: hidden !important;
        }

        div[data-testid="stTable"] table {
            width: 100% !important;
            table-layout: auto !important; /* Deixa o navegador calcular o melhor ajuste */
            background-color: white !important;
            color: black !important;
            border-collapse: collapse !important;
        }

        /* Diminuição agressiva da fonte e padding para caber tudo */
        div[data-testid="stTable"] th, div[data-testid="stTable"] td {
            border: 1px solid #000 !important;
            padding: 2px 4px !important; /* Espaço interno mínimo */
            font-size: 8px !important;    /* Fonte bem pequena para não forçar a largura */
            color: black !important;
            vertical-align: top !important;
            line-height: 1.1 !important;
            white-space: normal !important; /* Força o texto a quebrar linha sempre que possível */
            word-break: break-all !important; /* Permite quebrar palavras se necessário para não vazar */
        }

        /* Cabeçalho superior */
        div[data-testid="stTable"] thead tr th {
            background-color: #f2f2f2 !important;
            font-weight: bold !important;
            text-align: center !important;
        }

        /* Garante que o fundo seja sempre branco */
        div[data-testid="stTable"] tr {
            background-color: white !important;
        }

        /* Ajuste específico para colunas de identificação não sumirem */
        div[data-testid="stTable"] tr th:nth-child(1), 
        div[data-testid="stTable"] tr td:nth-child(1) {
            min-width: 30px !important; /* Largura mínima para o ANO */
        }
        </style>
        """, unsafe_allow_html=True)

    st.write("### 📋 Relatório")
    st.table(tabela_visual)
