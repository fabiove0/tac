# ==========================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO
# ==========================================================
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import base64

st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("Painel de Monitoramento de TACs")

# ==========================================================
# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
# ==========================================================
url = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/"
    "pub?gid=0&single=true&output=csv"
)

df = pd.read_csv(url)
df_tratado = df.fillna('')

def normalizar_texto(x):
    if isinstance(x, str):
        x = x.replace('\\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
        x = ' '.join(x.splitlines())
        x = ' '.join(x.split())
    return x

df_tratado = df_tratado.applymap(normalizar_texto)

# Função para SOMBREAMENTO (Destaque) apenas no App
def estilizar_status_app(texto):
    if not texto or not isinstance(texto, str):
        return texto
    t = texto.upper().strip()
    bg = None
    if "CONCLUÍDO" in t or "CUMPRIDO" in t:
        bg = "#d4edda"  # Verde claro
    elif "EM ANDAMENTO" in t or "EM EXECUÇÃO" in t:
        bg = "#fff3cd"  # Amarelo claro
    elif "NÃO INICIADO" in t or "ATRASADO" in t:
        bg = "#f8d7da"  # Vermelho claro
    elif "NÃO SE APLICA" in t:
        bg = "#e2e3e5"  # Cinza claro
    
    if bg:
        return f'<span style="background-color: {bg}; padding: 2px 4px; border-radius: 4px; font-weight: bold;">{texto}</span>'
    return texto

# Função para embutir a logo no HTML
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# ==========================================================
# 3. FILTROS E LÓGICA
# ==========================================================
mapa_titulos = {
    'ANO': 'Ano', 'DOCUMENTO': 'Documento', 'CLAUSULA': 'Cláusula',
    'COMPROMISSO_DA_CLAUSULA': 'Compromisso da Cláusula', 'STATUS_DA_CLAUSULA': 'Status da Cláusula',
    'OBS_SEJUS_CLAUSULA': 'Observações (SEJUS) – Cláusula', 'INCISO': 'Inciso',
    'COMPROMISSO_INCISO': 'Compromisso do Inciso', 'STATUS_DO_INCISO': 'Status do Inciso',
    'OBS_SEJUS_INCISO': 'Observações (SEJUS) – Inciso', 'ALINEA': 'Alínea',
    'COMPROMISSO_ALINEA': 'Compromisso da Alínea', 'STATUS_DA_ALINEA': 'Status da Alínea',
    'OBS_SEJUS_ALINEA': 'Observações (SEJUS) – Alínea'
}

lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.image("logo_sejus.png", use_container_width=True)
st.sidebar.header("Filtros")
escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)
termo_busca = st.text_input("🔍 Filtrar tabela por termo:", "")

tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[tabela_para_exibir['DOCUMENTO'] == escolha_tac]

if escolha_status != 'Todos':
    tabela_para_exibir = tabela_para_exibir[
        (tabela_para_exibir['STATUS_DA_CLAUSULA'] == escolha_status) |
        (tabela_para_exibir['STATUS_DO_INCISO'] == escolha_status) |
        (tabela_para_exibir['STATUS_DA_ALINEA'] == escolha_status)
    ]

if termo_busca:
    mask = tabela_para_exibir.astype(str).apply(
        lambda x: x.str.contains(termo_busca, case=False, na=False)
    ).any(axis=1)
    tabela_para_exibir = tabela_para_exibir[mask]

# ==========================================================
# 4. VISUALIZAÇÃO
# ==========================================================
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")
else:
    colunas_index = list(mapa_titulos.keys())

    # --- VERSÃO DOWNLOAD (LIMPA) ---
    tabela_visual_download = tabela_para_exibir.set_index(colunas_index)
    tabela_visual_download.index.names = [mapa_titulos[c] for c in tabela_visual_download.index.names]

    # --- VERSÃO APP (COM SOMBREAMENTO) ---
    tabela_app = tabela_para_exibir.copy()
    status_cols = ['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']
    for c in status_cols:
        if c in tabela_app.columns:
            tabela_app[c] = tabela_app[c].apply(estilizar_status_app)
    
    tabela_visual_app = tabela_app.set_index(colunas_index)
    tabela_visual_app.index.names = [mapa_titulos[c] for c in tabela_visual_app.index.names]

    # --- EXPORTAÇÃO HTML COM LOGO E BORDAS ---
    logo_b64 = get_base64_image("logo_sejus.png")
    logo_tag = f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;">' if logo_b64 else ""

    estilo_html_export = """
    <style>
        table { width: 100%; border-collapse: collapse; font-size: 10px; font-family: Arial; }
        th, td { border: 1px solid #444 !important; padding: 8px; vertical-align: top; }
        th { background-color: #f2f2f2; font-weight: bold; }
        thead tr:first-child { display: none; }
    </style>
    """
    html_tabela = tabela_visual_download.to_html(escape=False, index_names=True)
    html_final = f"<html><head><meta charset='UTF-8'>{estilo_html_export}</head><body><div style='display:flex;align-items:center;gap:15px;margin-bottom:20px;'>{logo_tag}<h1>Monitoramento de TACs</h1></div>{html_tabela}</body></html>"

    st.download_button("📄 Gerar Arquivo para Impressão (HTML)", html_final, "relatorio_tac.html", "text/html")

    # --- GRÁFICO COM CORES MAPEADAS ---
    col_status_data = tabela_para_exibir[['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']]
    lista_final = [x for x in col_status_data.stack() if x and x != 'NÃO SE APLICA']
    
    if len(lista_final) > 0:
        contagem = pd.Series(lista_final).value_counts()
        total_geral = len(lista_final)
        
        # Mapa de cores para a Pizza
        color_map = {
            "CONCLUÍDO": "#d4edda", "CUMPRIDO": "#d4edda",
            "EM ANDAMENTO": "#fff3cd", "EM EXECUÇÃO": "#fff3cd",
            "NÃO INICIADO": "#f8d7da", "ATRASADO": "#f8d7da",
            "NÃO SE APLICA": "#e2e3e5"
        }
        pie_colors = [color_map.get(s.upper(), "#e2e3e5") for s in contagem.index]

        def label_pizza(pct):
            val = int(round(total_geral / 100.0 * pct))
            return f"{pct:.1f}%\n({val} itens)"

        _, col_centro, _ = st.columns([1, 1, 1])
        with col_centro:
            fig, ax = plt.subplots(figsize=(3, 3))
            ax.pie(contagem.values, labels=contagem.index, autopct=label_pizza, 
                   startangle=140, textprops={'fontsize': 6}, colors=pie_colors)
            st.pyplot(fig)

    # --- TABELA NO APP (CSS ORIGINAL + SOMBREAMENTO) ---
    st.markdown("""
    <style>
        .tabela-relatorio { width: 100%; border-collapse: collapse; font-size: 10px; background-color: white; color: black; }
        .tabela-relatorio th, .tabela-relatorio td { border: 1px solid #444 !important; padding: 8px; vertical-align: top; }
        .tabela-relatorio th { font-weight: bold; text-align: center; background-color: #f2f2f2; }
        .tabela-relatorio thead tr:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)
    
    st.write("### 📋 Relatório")
    st.markdown(tabela_visual_app.to_html(escape=False, classes="tabela-relatorio", index_names=True), unsafe_allow_html=True)
