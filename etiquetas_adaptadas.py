import streamlit as st
import pandas as pd
from criacao_adaptadas import gerar_etiquetas
import re

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def limpar_nome_escola_simples(nome):
    """Função SUPER SIMPLES para limpar nomes - SEM PERDER ESCOLAS"""
    if pd.isna(nome):
        return nome
    
    nome = str(nome).upper().strip()
    
    # Remove códigos INEP se existirem
    nome = re.sub(r"\(INEP:\s*\d+\)", "", nome).strip()
    
    # Lista completa de siglas para remover - apenas remove do início
    siglas_para_remover = [
        "E.M.E.F. ",
        "E.M.E.I.F. ",
        "M.E.I.F ",
        "E M E I F ",
        "E M E F I ",
        "E M E F ", 
        "E M E I ",
        "C M E I ",
        "ESC EST ",
        "ESC ",
        "EMEF ",
        "EMEI ",
        "EMEIF ",
        "CMEI ",
        "CMEF ",
        "CMEIF ",
        "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL E INFANTIL ",
        "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL ",
        "ESCOLA MUNICIPAL DE ENSINO INFANTIL ",
        "ESCOLA MUNICIPAL ",
        "CENTRO MUNICIPAL DE EDUCACAO INFANTIL ",
        "CENTRO MUNICIPAL ",
        "ESCOLA ",
        "ESC MUNICIPAL ",
        "Escola M.E.I.F ",
        "ESC MUN ",
        "E I F ",
        "E F "
    ]
    
    # Remover apenas se começar com a sigla E sobrar nome decente
    nome_original = nome
    for sigla in siglas_para_remover:
        if nome.startswith(sigla):
            nome_sem_sigla = nome[len(sigla):].strip()
            if len(nome_sem_sigla) > 3:  # Só aceita se sobrar um nome
                nome = nome_sem_sigla
                break
    
    # Se deu algo errado, volta pro original
    if len(nome) < 3:
        nome = nome_original
        
    return nome

def detectar_colunas_automaticamente(df):
    """Detecta automaticamente as colunas da planilha adaptadas"""
    
    # Normalizar nomes das colunas
    df.columns = [col.upper().strip() for col in df.columns]
    
    # Mapear colunas conhecidas
    mapeamento = {}
    
    # Detectar coluna da escola
    for col in df.columns:
        if any(palavra in col.upper() for palavra in ['ESCOLA', 'NOME']):
            mapeamento[col] = 'NOME ESCOLA'
            break
    
    # Detectar outras colunas
    for col in df.columns:
        col_upper = col.upper()
        if 'CATEGORIA' in col_upper or 'DEFICIENCIA' in col_upper:
            mapeamento[col] = 'CATEGORIA'
        elif 'ANO' in col_upper and col not in mapeamento:
            mapeamento[col] = 'ANO ESCOLAR'
        elif any(palavra in col_upper for palavra in ['QUANTIDADE', 'TOTAL', 'QTD']):
            mapeamento[col] = 'TOTAL'
    
    # Se não encontrou escola
    if 'NOME ESCOLA' not in mapeamento.values():
        return None, "Coluna com nome da escola não encontrada!"
    
    return mapeamento, None

def interface_adaptadas():
    st.header("Etiquetas - Provas Adaptadas")

    # Exemplo de tabela esperada
    exemplo = {
        "Escola": ["ESCOLA MUNICIPAL PEIXE-BOI"],
        "Categoria": ["TEA"],
        "Ano": ["5º"],
        "Quantidade": ["10"]
    }
    st.markdown("### 📊 Estrutura esperada da planilha:")
    st.dataframe(pd.DataFrame(exemplo), hide_index=True)

    uploaded_file = st.file_uploader("Carregue sua planilha (CSV ou Excel)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            # Carregar arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Detectar colunas automaticamente
            mapeamento, erro = detectar_colunas_automaticamente(df)
            
            if erro:
                st.error(f"❌ {erro}")
                st.info("💡 Verifique se sua planilha contém uma coluna com nome da escola")
                st.stop()
            
            # Aplicar mapeamento
            df_mapeado = df.rename(columns=mapeamento)
            
            # Verificar colunas obrigatórias
            required_columns = ['NOME ESCOLA']
            missing_columns = [col for col in required_columns if col not in df_mapeado.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                st.info("💡 Verifique se sua planilha contém pelo menos uma coluna com nome da escola")
                st.stop()

            # Criar colunas padrão se não existirem
            if 'CATEGORIA' not in df_mapeado.columns:
                df_mapeado['CATEGORIA'] = 'GERAL'
            if 'ANO ESCOLAR' not in df_mapeado.columns:
                df_mapeado['ANO ESCOLAR'] = 'NÃO INFORMADO'
            if 'TOTAL' not in df_mapeado.columns:
                df_mapeado['TOTAL'] = 1

            # Processar dados
            df_mapeado['ANO ESCOLAR'] = df_mapeado['ANO ESCOLAR'].astype(str).str.strip()
            
            # Adicionar "ANO" se não for EJAI
            mask = ~df_mapeado['ANO ESCOLAR'].str.upper().str.contains("EJAI", na=False)
            mask = mask & ~df_mapeado['ANO ESCOLAR'].str.upper().str.contains("ANO", na=False)
            df_mapeado.loc[mask, 'ANO ESCOLAR'] += " ANO"

            # Processar coluna TOTAL
            df_mapeado['TOTAL'] = pd.to_numeric(df_mapeado['TOTAL'], errors='coerce').fillna(1).astype(int)
            df_transformado = df_mapeado[df_mapeado['TOTAL'] > 0].copy()

            # Limpar nomes das escolas usando a nova função
            df_transformado["NOME ESCOLA"] = df_transformado['NOME ESCOLA'].apply(limpar_nome_escola_simples)
            
            df_transformado = df_transformado.sort_values(by='NOME ESCOLA').reset_index(drop=True)

            # Verificar se há dados válidos
            if df_transformado.empty:
                st.warning("⚠️ Não foram encontrados dados válidos na planilha!")
                st.stop()

            # Mostrar resumo dos dados processados
            st.markdown("### 📈 Resumo dos Dados Processados:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Escolas", df_transformado['NOME ESCOLA'].nunique())
            with col2:
                st.metric("Anos/Turmas", df_transformado['ANO ESCOLAR'].nunique())
            with col3:
                st.metric("Total de Alunos", df_transformado['TOTAL'].sum())

            st.markdown("### 📋 Dados Processados:")
            st.dataframe(df_transformado, use_container_width=True, hide_index=True)

            st.download_button(
                "📥 Baixar arquivo transformado (CSV)", 
                convert_df(df_transformado), 
                "dados_transformados.csv", 
                "text/csv"
            )

            # Seção para gerar PDF
            st.markdown("### 🏷️ Gerar Etiquetas PDF")
            logo_file = st.file_uploader("Carregue a imagem da logo para o PDF (formato JPEG)", type=["jpg", "jpeg"])
            campeonato = st.text_input("Nome do Campeonato").upper()
            etapa = st.text_input("Etapa").upper()

            if logo_file and campeonato and etapa:
                try:
                    pdf_data = gerar_etiquetas(df_transformado, logo_file, campeonato, etapa)
                    st.download_button(
                        label="📥 Baixar PDF de Etiquetas",
                        data=pdf_data,
                        file_name='etiquetas_adaptadas.pdf',
                        mime='application/pdf'
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar planilha: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato correto e tente novamente.")