import streamlit as st
import pandas as pd
from criacao_nao_adaptadas import gerar_etiquetas
import re

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def limpar_nome_escola(escola):
    """Remove siglas e códigos INEP dos nomes das escolas"""
    if pd.isna(escola):
        return escola
    
    escola_original = str(escola).strip()
    escola = escola_original.upper()  # Trabalhar em maiúsculas para facilitar
    
    # Remover códigos INEP
    escola = re.sub(r"\(INEP:\s*\d+\)", "", escola, flags=re.IGNORECASE).strip()
    
    # Lista de siglas para remover do início (mais conservadora)
    siglas_patterns = [
        # Siglas com espaços entre letras - mais específicas
        r"^E\s+M\s+E\s+I\s+F\s+",  # E M E I F (com espaços obrigatórios)
        r"^E\s+M\s+E\s+F\s+",      # E M E F (com espaços obrigatórios)
        r"^E\s+M\s+E\s+I\s+",      # E M E I (com espaços obrigatórios)  
        r"^C\s+M\s+E\s+I\s+",      # C M E I (com espaços obrigatórios)
        
        # Siglas sem espaços - versões completas primeiro
        r"^ESCOLA\s+MUNICIPAL\s+DE\s+ENSINO\s+FUNDAMENTAL\s+E\s+INFANTIL\s+",
        r"^ESCOLA\s+MUNICIPAL\s+DE\s+ENSINO\s+FUNDAMENTAL\s+",
        r"^ESCOLA\s+MUNICIPAL\s+DE\s+ENSINO\s+INFANTIL\s+",
        r"^ESCOLA\s+MUNICIPAL\s+",
        r"^CENTRO\s+MUNICIPAL\s+DE\s+EDUCACAO\s+INFANTIL\s+",
        r"^CENTRO\s+MUNICIPAL\s+",
        r"^ESC\s+MUNICIPAL\s+",
        r"^ESC\s+MUN\s+",
        r"^CMEBI\s+",
        r"^CMEI\s+", 
        r"^CMEF\s+",
        r"^EMEI\s+",
        r"^EMEF\s+",
        
        # Siglas isoladas com espaços - apenas no final
        r"^E\s+I\s+F\s+",         # E I F
        r"^E\s+F\s+",             # E F
        r"^EJA\s+",
        r"^EM\s+(?!E)",           # EM mas não quando seguido de E (evita remover de "EM ESPERANÇA")
    ]
    
    # Aplicar remoção das siglas com mais cuidado
    for pattern in siglas_patterns:
        if re.match(pattern, escola, flags=re.IGNORECASE):
            escola_nova = re.sub(pattern, "", escola, flags=re.IGNORECASE).strip()
            # Verificar se sobrou um nome válido
            if len(escola_nova) >= 5:  # Aumentei o mínimo para 5 caracteres
                escola = escola_nova
                break
    
    # Limpeza final muito suave
    escola = re.sub(r'\s+', ' ', escola).strip()
    
    # Se o nome ficou muito pequeno ou vazio, retorna o original
    if len(escola) < 5:
        return escola_original.upper().strip()
    
    return escola

def interface_nao_adaptadas():
    st.header("Etiquetas - Provas Não Adaptadas")

    # Lista de colunas esperadas
    st.markdown("### 📋 Colunas esperadas na planilha:")
    st.markdown("**Coluna obrigatória:**")
    st.code("Qual é o nome da sua escola?")
    
    st.markdown("**Colunas opcionais (anos escolares):**")
    colunas_esperadas = [
        "Total de alunos do 1º ano da MANHÃ",
        "Total de alunos do 1º ano da TARDE", 
        "Total de alunos do 2º ano da MANHÃ",
        "Total de alunos do 2º ano da TARDE",
        "Total de alunos do 3º ano da MANHÃ",
        "Total de alunos do 3º ano da TARDE",
        "Total de alunos do 4º ano da MANHÃ", 
        "Total de alunos do 4º ano da TARDE",
        "Total de alunos do 5º ano da MANHÃ",
        "Total de alunos do 5º ano da TARDE",
        "Total de alunos do 6º ano da MANHÃ",
        "Total de alunos do 6º ano da TARDE",
        "Total de alunos do 7º ano da MANHÃ",
        "Total de alunos do 7º ano da TARDE", 
        "Total de alunos do 8º ano da MANHÃ",
        "Total de alunos do 8º ano da TARDE",
        "Total de alunos do 9º ano da MANHÃ",
        "Total de alunos do 9º ano da TARDE",
        "Total de alunos da EJAI 1ª TOTALIDADE",
        "Total de alunos da EJAI 2ª TOTALIDADE",
        "Total de alunos da EJAI 3ª TOTALIDADE", 
        "Total de alunos da EJAI 4ª TOTALIDADE"
    ]
    
    # Criar texto copiável com todas as colunas
    texto_colunas = "Qual é o nome da sua escola?\n" + "\n".join(colunas_esperadas)
    
    with st.expander("📝 Copiar nomes das colunas"):
        st.text_area(
            "Cole estes nomes no cabeçalho da sua planilha:", 
            texto_colunas, 
            height=200,
            help="Você pode usar apenas algumas dessas colunas, não precisa usar todas!"
        )

    # Exemplo de tabela esperada
    exemplo = {
        "Qual é o nome da sua escola?": ["ESCOLA MUNICIPAL PEIXE-BOI"],
        "Total de alunos do 1º ano da MANHÃ": [25],
        "Total de alunos do 1º ano  da TARDE": [20],
        "Total de alunos do 2º  ano da MANHÃ": [30],
        "Total de alunos do 2º  ano da TARDE": [28],
    }
    st.markdown("### 📊 Estrutura esperada da planilha:")
    st.dataframe(pd.DataFrame(exemplo))

    uploaded_file = st.file_uploader("Carregar planilha CSV", type="csv")

    if uploaded_file:
        try:
            labels_df = pd.read_csv(uploaded_file)
            
            # Mapeamento completo de colunas
            rename_map = {
                'Qual é o nome da sua escola?': 'NOME ESCOLA',
                'Total de alunos do 1º ano da MANHÃ': '1º ANO MANHÃ',
                'Total de alunos do 1º ano da TARDE': '1º ANO TARDE',
                'Total de alunos do 2º ano da MANHÃ': '2º ANO MANHÃ',
                'Total de alunos do 2º ano da TARDE': '2º ANO TARDE',
                'Total de alunos do 3º ano da MANHÃ': '3º ANO MANHÃ',
                'Total de alunos do 3º ano da TARDE': '3º ANO TARDE',
                'Total de alunos do 4º ano da MANHÃ': '4º ANO MANHÃ',
                'Total de alunos do 4º ano da TARDE': '4º ANO TARDE',
                'Total de alunos do 5º ano da MANHÃ': '5º ANO MANHÃ',
                'Total de alunos do 5º ano da TARDE': '5º ANO TARDE',
                'Total de alunos do 6º ano da MANHÃ': '6º ANO MANHÃ',
                'Total de alunos do 6º ano da TARDE': '6º ANO TARDE',
                'Total de alunos do 7º ano da MANHÃ': '7º ANO MANHÃ',
                'Total de alunos do 7º ano da TARDE': '7º ANO TARDE',
                'Total de alunos do 8º ano da MANHÃ': '8º ANO MANHÃ',
                'Total de alunos do 8º ano da TARDE': '8º ANO TARDE',
                'Total de alunos do 9º ano da MANHÃ': '9º ANO MANHÃ',
                'Total de alunos do 9º ano da TARDE': '9º ANO TARDE',
                'Total de alunos da EJAI 1ª TOTALIDADE': 'EJAI 1º ANO',
                'Total de alunos da EJAI 2ª TOTALIDADE': 'EJAI 2º ANO',
                'Total de alunos da EJAI 3ª TOTALIDADE': 'EJAI 3º ANO',
                'Total de alunos da EJAI 4ª TOTALIDADE': 'EJAI 4º ANO'
            }
            
            # Verificar se a coluna obrigatória existe
            if 'Qual é o nome da sua escola?' not in labels_df.columns:
                st.error("❌ A coluna 'Qual é o nome da sua escola?' é obrigatória!")
                st.stop()
            
            # Identificar quais colunas estão presentes na planilha
            colunas_presentes = [col for col in rename_map.keys() if col in labels_df.columns]
            
            # Renomear apenas as colunas que existem
            colunas_para_renomear = {k: v for k, v in rename_map.items() if k in labels_df.columns}
            labels_df.rename(columns=colunas_para_renomear, inplace=True)
            
            # Selecionar apenas as colunas que existem
            colunas_existentes = ['NOME ESCOLA'] + [rename_map[col] for col in colunas_presentes if col != 'Qual é o nome da sua escola?']
            new_df = labels_df[colunas_existentes].copy()
            
            # Transformar dados (melt)
            colunas_anos = [col for col in colunas_existentes if col != 'NOME ESCOLA']
            
            if not colunas_anos:
                st.warning("⚠️ Nenhuma coluna de ano escolar foi encontrada na planilha!")
                st.stop()
            
            newnew_df = new_df.melt(
                id_vars=['NOME ESCOLA'], 
                value_vars=colunas_anos,
                var_name='ANO ESCOLAR', 
                value_name="TOTAL"
            )
            
            # Limpar e processar dados
            clean_df = newnew_df.copy()
            clean_df = clean_df.dropna()
            clean_df["TOTAL"] = pd.to_numeric(clean_df["TOTAL"], errors='coerce').fillna(0).astype(int)
            clean_df = clean_df[clean_df["TOTAL"] > 0]

            if clean_df.empty:
                st.warning("⚠️ Não foram encontrados dados válidos (valores maiores que 0) na planilha!")
                st.stop()

            # Aplicar a função corrigida de limpeza dos nomes das escolas
            # Debug: contar escolas antes da limpeza
            escolas_antes = new_df['NOME ESCOLA'].nunique()
            escolas_originais_lista = new_df['NOME ESCOLA'].unique()
            
            clean_df["NOME ESCOLA"] = clean_df['NOME ESCOLA'].apply(limpar_nome_escola)
            clean_df = clean_df.sort_values(by='NOME ESCOLA').reset_index(drop=True)
            
            # Debug: contar escolas depois da limpeza
            escolas_depois = clean_df['NOME ESCOLA'].nunique()
            
            # Se perdeu escolas, mostrar aviso
            if escolas_depois < escolas_antes:
                st.warning(f"⚠️ Atenção: {escolas_antes - escolas_depois} escola(s) foram perdidas na limpeza dos nomes. Total original: {escolas_antes}, Total após limpeza: {escolas_depois}")
                
                # Identificar quais escolas foram perdidas
                escolas_processadas = set()
                for escola_original in escolas_originais_lista:
                    escola_limpa = limpar_nome_escola(escola_original)
                    if len(escola_limpa) >= 5:  # Só adiciona se passou na validação
                        escolas_processadas.add(escola_limpa)
                
                escolas_originais_set = set(escolas_originais_lista)
                
                with st.expander("🚨 VER ESCOLAS PERDIDAS - CLIQUE AQUI"):
                    st.write("**📊 Resumo:**")
                    st.write(f"- Escolas na planilha original: {len(escolas_originais_set)}")
                    st.write(f"- Escolas após processamento: {len(escolas_processadas)}")
                    st.write(f"- Escolas perdidas: {len(escolas_originais_set) - len(escolas_processadas)}")
                    
                    st.write("**🔍 Análise detalhada das primeiras 15 escolas:**")
                    for i, escola in enumerate(list(escolas_originais_lista)[:15]):
                        escola_limpa = limpar_nome_escola(escola)
                        status = "✅ OK" if len(escola_limpa) >= 5 else "❌ PERDIDA"
                        
                        st.write(f"**{i+1}.** {status}")
                        st.write(f"   📝 Original: `{escola}`")
                        st.write(f"   🔧 Processado: `{escola_limpa}` (tamanho: {len(escola_limpa)})")
                        
                        if len(escola_limpa) < 5:
                            st.write(f"   ⚠️ **MOTIVO DA PERDA:** Nome muito curto após limpeza")
                        
                        st.write("---")

            # Mostrar resumo dos dados
            st.markdown("### 📈 Resumo dos Dados Processados:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Escolas", clean_df['NOME ESCOLA'].nunique())
            with col2:
                st.metric("Anos/Turmas", clean_df['ANO ESCOLAR'].nunique())
            with col3:
                st.metric("Total de Alunos", clean_df['TOTAL'].sum())

            # Exibir dados processados usando st.dataframe em vez de AgGrid
            st.markdown("### 📋 Dados Processados:")
            st.dataframe(clean_df, use_container_width=True, hide_index=True)



            st.download_button(
                "📥 Baixar Planilha Tratada", 
                convert_df(clean_df), 
                "base_dados_tratados.csv", 
                "text/csv"
            )

            # Seção para gerar PDF
            st.markdown("### 🏷️ Gerar Etiquetas PDF")
            logo_file = st.file_uploader("Carregue a imagem da logo (formato JPEG)", type=["jpg", "jpeg"])
            championship = st.text_input("Nome do Campeonato").upper()
            stage = st.text_input("Etapa").upper()

            if logo_file and championship and stage:
                try:
                    pdf_data = gerar_etiquetas(clean_df, logo_file, championship, stage)
                    st.download_button(
                        label="📥 Baixar PDF das Etiquetas",
                        data=pdf_data,
                        file_name='etiquetas.pdf',
                        mime='application/pdf'
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar planilha: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato correto e tente novamente.")