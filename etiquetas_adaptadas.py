import streamlit as st
import pandas as pd
from criacao_adaptadas import gerar_etiquetas
import re

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def limpar_nome_escola(escola):
    """Remove siglas e códigos INEP dos nomes das escolas"""
    escola = re.sub(r"\(INEP:\s*\d+\)", "", str(escola), flags=re.IGNORECASE).strip()
    escola = re.sub(r"\b([A-Z])\s+([A-Z])\b", r"\1\2", escola)
    siglas = ["CMEI", "EMEI", "EMEF", "EM", "EJA", "CMEF", "CMEBI"]
    padrao = r"^(?:" + "|".join(siglas) + r")\s+"
    return re.sub(padrao, "", escola, flags=re.IGNORECASE).strip()

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
    # CORREÇÃO 1: Adicionar hide_index=True para remover os números do índice
    st.dataframe(pd.DataFrame(exemplo), hide_index=True)

    uploaded_file = st.file_uploader("Carregue sua planilha (CSV ou Excel)", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            # Carregar arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Normalizar nomes das colunas
            df.columns = [col.upper() for col in df.columns]
            
            # Renomear colunas para padrão interno
            df = df.rename(columns={
                'ESCOLA': 'NOME ESCOLA', 
                'ANO': 'ANO ESCOLAR', 
                'CATEGORIA': 'CATEGORIA',
                'QUANTIDADE': 'TOTAL'
            })
            
            # Verificar se as colunas obrigatórias existem
            required_columns = ['NOME ESCOLA', 'CATEGORIA', 'ANO ESCOLAR']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
                st.info("💡 Verifique se sua planilha contém as colunas: Escola, Categoria, Ano, Quantidade")
                st.stop()

            # Processar dados
            df['ANO ESCOLAR'] = df['ANO ESCOLAR'].astype(str).str.strip()
            df.loc[~df['ANO ESCOLAR'].str.upper().str.contains("EJAI"), 'ANO ESCOLAR'] += " ANO"

            # Identificar coluna de quantidade
            col_qtd = [c for c in df.columns if df[c].dtype in ['int64', 'float64']]
            if col_qtd:
                quantidade_col = col_qtd[0]
                df[quantidade_col] = pd.to_numeric(df[quantidade_col], errors='coerce').fillna(0).astype(int)
                df_transformado = df[df[quantidade_col] > 0].copy()
                # Renomear para TOTAL se não for
                if quantidade_col != 'TOTAL':
                    df_transformado = df_transformado.rename(columns={quantidade_col: 'TOTAL'})
            else:
                df_transformado = df.copy()
                if 'TOTAL' not in df_transformado.columns:
                    df_transformado['TOTAL'] = 1  # Valor padrão se não houver coluna numérica

            # Limpar nomes das escolas (remover siglas)
            df_transformado["NOME ESCOLA"] = df_transformado['NOME ESCOLA'].apply(limpar_nome_escola).str.upper()
            
            # CORREÇÃO 2: Reset do índice para começar do 0 sequencialmente
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

            # CORREÇÃO 3: Exibir dados sem índice
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