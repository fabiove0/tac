# ... (dentro do seu 'else' de visualização)

# 1. Definimos colunas bem desbalanceadas (1 para gráfico, 4 para tabela)
col_grafico, col_tabela = st.columns([1, 4])

with col_grafico:
    st.write("### Resumo")
    if len(lista_final) > 0:
        contagem = pd.Series(lista_final).value_counts()
        
        # Diminuímos o figsize para o gráfico ficar pequeno e delicado
        fig, ax = plt.subplots(figsize=(3, 3)) 
        ax.pie(contagem.values, labels=contagem.index, autopct='%1.0f%%', 
               startangle=140, colors=plt.cm.Paired.colors, textprops={'fontsize': 8})
        
        # Removemos o título do gráfico para ganhar espaço, o st.write acima já serve
        st.pyplot(fig)

with col_tabela:
    st.write("### Detalhamento dos Compromissos")
    
    # Criamos a versão agrupada (indexada)
    # Dica: indexar apenas Ano, Documento e Cláusula para não "esmagar" a tabela
    tabela_visual = tabela_para_exibir.set_index(['ANO', 'DOCUMENTO', 'CLAUSULA'])
    
    # O PULO DO GATO: Usamos column_config para domar os textos longos
    st.dataframe(
        tabela_visual,
        use_container_width=True, # Faz a tabela ocupar todo o espaço da coluna 4
        column_config={
            "COMPROMISSO_DA_CLAUSULA": st.column_config.TextColumn("Compromisso", width="large"),
            "COMPROMISSO_INCISO": st.column_config.TextColumn("Compromisso Inciso", width="large"),
            "OBS_SEJUS_CLAUSULA": st.column_config.TextColumn("Observações", width="medium"),
        }
    )
