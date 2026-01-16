# ==========================================================
# IMPORTAÇÕES
# ==========================================================
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import base64


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(page_title="Monitoramento de TACs", layout="wide")
st.title("Painel de Monitoramento de TACs")


# ==========================================================
# CARREGAMENTO DOS DADOS
# ==========================================================
url = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSzKqLRK17FmBUbOCv_DzHUqqXpSNJu8sfp2WNAHLfTBaUA0Eeq2WRSO9czpcfysEVfVCHtEsHkSygA/"
    "pub?gid=0&single=true&output=csv"
)

df = pd.read_csv(url)
df_tratado = df.fillna('')


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================
def normalizar_texto(x):
    if isinstance(x, str):
        x = x.replace('\\n', '\n')
        x = x.replace('\r\n', '\n')
        x = x.replace('\r', '\n')
        x = ' '.join(x.splitlines())
        x = ' '.join(x.split())
    return x


def fazer_rotulo(pct):
    resultado = int(round(total_geral / 100.0 * pct))
    return f"{pct:.1f}%\n({resultado} itens)"
    
def estilizar_status(texto):
    if not texto or not isinstance(texto, str):
        return texto
    
    t = texto.upper().strip()
    bg = None
    cor_fonte = "black" # Define um padrão para evitar NameError
    
    if "CONCLUÍDO" in t or "CUMPRIDO" in t:
        bg = "#C6EFCE"; cor_fonte = "#006100"
    elif "EM EXECUÇÃO" in t or "EM EXECUÇAO" in t or "EM EXECUCAO" in t or "EM ANDAMENTO" in t:
        bg = "#FFEB9C"; cor_fonte = "#9C6500"
    elif "NÃO INICIADO" in t or "NAO INICIADO" in t or "ATRASADO" in t:
        bg = "#FFC7CE"; cor_fonte = "#9C0006"
    elif "NÃO SE APLICA" in t or "NAO SE APLICA" in t:
        bg = "#E7E7E7"; cor_fonte = "#333333"
    
    if bg:
        return f'<span style="background-color: {bg}; color: {cor_fonte}; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{texto}</span>'
    return texto
def converter_imagem_para_base64(caminho_da_imagem):
    try:
        with open(caminho_da_imagem, "rb") as arquivo_imagem:
            # Transforma os bytes da imagem em uma string de texto Base64
            conteudo = arquivo_imagem.read()
            return base64.b64encode(conteudo).decode()
    except Exception as e:
        return None


# ==========================================================
# TRATAMENTO DOS DADOS
# ==========================================================
df_tratado = df_tratado.applymap(normalizar_texto)


# ==========================================================
# MAPA DE NOMES AMIGÁVEIS (APENAS VISUAL)
# ==========================================================
mapa_titulos = {
    'ANO': 'Ano',
    'DOCUMENTO': 'Documento',
    'CLAUSULA': 'Cláusula',
    'COMPROMISSO_DA_CLAUSULA': 'Compromisso da Cláusula',
    'STATUS_DA_CLAUSULA': 'Status da Cláusula',
    'OBS_SEJUS_CLAUSULA': 'Observações (SEJUS) – Cláusula',
    'INCISO': 'Inciso',
    'COMPROMISSO_INCISO': 'Compromisso do Inciso',
    'STATUS_DO_INCISO': 'Status do Inciso',
    'OBS_SEJUS_INCISO': 'Observações (SEJUS) – Inciso',
    'ALINEA': 'Alínea',
    'COMPROMISSO_ALINEA': 'Compromisso da Alínea',
    'STATUS_DA_ALINEA': 'Status da Alínea',
    'OBS_SEJUS_ALINEA': 'Observações (SEJUS) – Alínea'
}


# ==========================================================
# FILTROS (SIDEBAR)
# ==========================================================
lista_tacs = ['Todos'] + sorted(df_tratado['DOCUMENTO'].unique().tolist())
lista_status = ['Todos'] + sorted(df_tratado['STATUS_DA_CLAUSULA'].unique().tolist())

st.sidebar.image("logo_sejus.png", use_container_width=True)
st.sidebar.header("Filtros")

escolha_tac = st.sidebar.selectbox("Selecione o Documento:", lista_tacs)
escolha_status = st.sidebar.selectbox("Selecione o Status:", lista_status)
st.sidebar.markdown("""
    <hr style="margin: 10px 0; border: 0.5px solid #88888855;">
    <div style="line-height: 1.6; font-weight: 700;">
        <div style="font-size: 13px; margin-bottom: 5px;">
            NGER - Núcleo de Gestão Estratégica para Resultados
        </div>
        <div style="font-size: 11px; font-weight: 600; opacity: 0.8;">
            Equipe: Amanda L. B. Silva, Ana C. P. Silva, Bernardo M. Filho, 
            Daiane B. Fernandes, Débora F. Pimenta e Nicole Garcia nger@sejus.mt.gov.br
        </div>
        <div style="margin-top: 10px; font-size: 11px; border-top: 1px dotted #88888855; padding-top: 8px;">
            Desenvolvedor: Fabio V. Lima
        </div>
    </div>
""", unsafe_allow_html=True)


termo_busca = st.text_input("🔍 Filtrar tabela por termo:", "")


# ==========================================================
# LÓGICA DE FILTRAGEM
# ==========================================================
tabela_para_exibir = df_tratado.copy()

if escolha_tac != 'Todos':
    tabela_para_exibir = tabela_para_exibir[
        tabela_para_exibir['DOCUMENTO'] == escolha_tac
    ]

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
# VISUALIZAÇÃO
# ==========================================================
if len(tabela_para_exibir) == 0:
    st.warning("Nenhum dado encontrado com esse filtro.")

else:
    # --- 1. PREPARAÇÃO DA TABELA PARA O APP (COM CORES) ---
    tabela_visual_estilizada = tabela_para_exibir.copy()
    
    colunas_status = ['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']
    for col in colunas_status:
        if col in tabela_visual_estilizada.columns:
            tabela_visual_estilizada[col] = tabela_visual_estilizada[col].apply(estilizar_status)
    
    colunas_index = list(mapa_titulos.keys())
    
    # Criamos a tabela_visual (esta sim terá os 14 índices)
    tabela_visual = tabela_visual_estilizada.set_index(colunas_index)

    # CORREÇÃO AQUI: Aplicar os nomes na tabela_visual, não na estilizada
    tabela_visual.index.names = [mapa_titulos[c] for c in tabela_visual.index.names]
    
    # --- 2. PREPARAÇÃO DA TABELA PARA DOWNLOAD (LIMPA) ---
    tabela_print_visual = tabela_para_exibir.set_index(colunas_index)
    tabela_print_visual.index.names = [mapa_titulos[c] for c in tabela_print_visual.index.names]

    # ======================================================
    # CSS DA TABELA (APP)
    # ======================================================
    st.markdown("""
    <style>
        .tabela-relatorio {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            table-layout: auto;
            background-color: white;
            color: black;
        }

        .tabela-relatorio th,
        .tabela-relatorio td {
            border: 1px solid #444;
            padding: 8px;
            vertical-align: top;
            white-space: normal;
            word-break: keep-all;
            overflow-wrap: normal;
        }

        .tabela-relatorio th {
            font-weight: bold;
            text-align: center;
        }

        .tabela-relatorio thead tr:first-child {
            display: none;
        }

    </style>
    """, unsafe_allow_html=True)


    # ======================================================
    # EXPORTAÇÃO HTML
    # ======================================================
    estilo_html_export = """
    <style>
    body { font-family: Arial, sans-serif; }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 9px;
        table-layout: auto;
    }

    th, td {
        border: 1px solid #444;
        padding: 6px;
        vertical-align: top;
    }

    thead tr:first-child { display: none; }
    /* Estilos do Cabeçalho Oficial */
    .header-table {
        width: 100%;
        border: none !important;
        border-collapse: collapse;
        margin-bottom: 10px;

    }

    .header-table td {
        border: none !important;
        vertical-align: middle;
        padding: 0;

    }

    /* Definindo larguras iguais para os lados para centralizar o meio */

    .logo-container { 
        width: 20%; 
        text-align: left; 
    }

    .titles-container { 
        width: 60%; 
        text-align: center; 
    }

    .date-container { 
        text-align: center;
        font-size: 9px;
        color: #333;
        margin-top: 10px;
        margin-bottom: 15px;
        line-height: 1.4;
        font-style: italic;
    }
    
    .spacer-container { 
        width: 20%; 
    }
    

    .main-title { 

        font-size: 15px; 
        font-weight: bold; 
        margin-bottom: 2px; 
    }

    .sub-title { 
        font-size: 12px; 
        font-weight: normal; 
    }
    .methodology {
        text-align: center;
        font-size: 9px;
        color: #333;
        margin-top: 10px;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    hr { border: 0; border-top: 1px solid #000; margin: 5px 0; }

</style>
"""

    html_tabela = tabela_print_visual.to_html(
        escape=False,
        index_names=True
    )

    # 1. Busca a imagem e converte (certifique-se de que o nome do arquivo está igual ao do GitHub)
    logo_base64 = converter_imagem_para_base64("logo_sejus.png")

    # 2. Cria a tag de imagem apenas se a conversão deu certo
    if logo_base64:
        img_tag = f'<img src="data:image/png;base64,{logo_base64}" style="height: 60px;">'
    else:
        img_tag = ""  # Caso dê erro, o HTML não quebra, apenas fica sem logo
        
    # Texto da metodologia exatamente como na imagem
    # Texto da metodologia
    texto_metodologia = """
    Monitoramento realizado conforme a metodologia descrita no presente relatório: textos do TAC e aditivos foram integralmente convertidos e inseridos nesta planilha mantendo-se fielmente o teor dos instrumentos originais; cada compromisso (cláusulas, incisos e alíneas) foi monitorado individualmente por sua especificidade; compromissos repetidos foram mantidos para preservar a integridade e rastreabilidade das informações.
    """
    texto_equipe = """
    Equipe (Amanda L. B. Silva, Ana C. P. Silva, Bernardo M. Filho, Daiane B. Fernandes, Débora F. Pimenta e Nicole Garcia) | Desenvolvedor: Fabio V. Lima
    """
    
    html_final = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            {estilo_html_export}
        </head>
        <body>
            <table class="header-table">
                <tr>
                    <td class="logo-container">
                        {img_tag}
                    </td>
                    <td class="titles-container">
                        <div class="main-title">NÚCLEO DE GESTÃO ESTRATÉGICA PARA RESULTADOS - NGER</div>
                        <div class="sub-title">MONITORAMENTO DA EXECUÇÃO DO TERMO DE AJUSTAMENTO DE CONDUTA - TAC/SISPEN</div>
                    </td>
                    <td class="spacer-container">
                        </td>
                </tr>
            </table>
            
            <hr style="border: 0.5px solid #000;">

            <div class="date-container">
                {texto_equipe}
            </div>
            
            <div class="methodology">
                {texto_metodologia}
            </div>
    
            {html_tabela}
        </body>
    </html>
    """

    st.download_button(
        "📄 Gerar Arquivo para Impressão (HTML)",
        html_final,
        "relatorio_tac.html",
        "text/html"
    )


    # ======================================================
    # GRÁFICO
    # ======================================================
    df_grafico = tabela_para_exibir.melt(
    id_vars=["DOCUMENTO"],
    value_vars=[
        "STATUS_DA_CLAUSULA",
        "STATUS_DO_INCISO",
        "STATUS_DA_ALINEA"
    ],
    var_name="TIPO",
    value_name="STATUS"
    )

    df_grafico = df_grafico[
        (df_grafico["STATUS"] != "") &
        (df_grafico["STATUS"] != "NÃO SE APLICA")
    ]
    
    df_grafico["STATUS"] = df_grafico["STATUS"].str.upper()
    
    contagem_tac_status = (
    df_grafico
    .groupby(["DOCUMENTO", "STATUS"])
    .size()
    .reset_index(name="TOTAL")
    )
    tabela_pivot = (
    contagem_tac_status
    .pivot(index="DOCUMENTO", columns="STATUS", values="TOTAL")
    .fillna(0)
    )
    
    mapa_cores = {
    "CONCLUÍDO": "#C6EFCE", 
    "CUMPRIDO": "#C6EFCE",
    "EM EXECUÇÃO": "#FFEB9C", 
    "EM EXECUÇAO": "#FFEB9C",
    "EM ANDAMENTO": "#FFEB9C",
    "NÃO INICIADO": "#FFC7CE", 
    "NAO INICIADO": "#FFC7CE",
    "ATRASADO": "#FFC7CE",
    "NÃO SE APLICA": "#E7E7E7"
    }
    
    col_status = tabela_para_exibir[
        ['STATUS_DA_CLAUSULA', 'STATUS_DO_INCISO', 'STATUS_DA_ALINEA']
    ]

    lista_final = [
        x for x in col_status.stack()
        if x and x != 'NÃO SE APLICA'
    ]

    contagem = pd.Series(lista_final).value_counts()
    total_geral = len(lista_final)

    cores_do_grafico = [mapa_cores.get(status.upper(), "#D3D3D3") for status in contagem.index]
    

    col1, col2 = st.columns([1, 2])
    with col1:
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.pie(
            contagem.values, 
            labels=contagem.index, 
            autopct=fazer_rotulo, 
            startangle=140, 
            textprops={'fontsize': 6},
            colors=cores_do_grafico  
        )
        st.pyplot(fig)
    with col2:
        fig_barra, ax_barra = plt.subplots(figsize=(4, 1))
    
        bottom = None
    
        for status, cor in mapa_cores.items():
            if status in tabela_pivot.columns:
                valores = tabela_pivot[status]
    
                barras = ax_barra.bar(
                    tabela_pivot.index,
                    valores,
                    bottom=bottom,
                    color=cor
                )
    
                # ESCREVER NÚMEROS DENTRO DAS BARRAS
                for i, valor in enumerate(valores):
                    if valor > 0:
                        y_pos = valor / 2 if bottom is None else bottom[i] + valor / 2
                        ax_barra.text(
                            i,
                            y_pos,
                            int(valor),
                            ha="center",
                            va="center",
                            fontsize=4,
                            color="black",
                            fontweight="bold"
                        )
    
                bottom = valores if bottom is None else bottom + valores
    
        ax_barra.set_title("Distribuição de Status por TAC")
        ax_barra.legend().remove()          # remove legenda
        ax_barra.set_xlabel("")             # remove título eixo X
        ax_barra.set_ylabel("")             # remove título eixo Y
        ax_barra.set_yticks([])
        ax_barra.tick_params(axis='x', rotation=45, labelsize=7)

        ax_barra.legend(fontsize=3)

        st.pyplot(fig_barra)
    # ======================================================
    # TABELA FINAL (APP)
    # ======================================================
    st.write("### 📋 Relatório")

    st.markdown(
        tabela_visual.to_html(
            escape=False,
            classes="tabela-relatorio",
            index_names=True
        ),
        unsafe_allow_html=True
    )
