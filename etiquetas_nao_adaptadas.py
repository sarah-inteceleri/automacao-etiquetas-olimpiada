import streamlit as st
import pandas as pd
from criacao_nao_adaptadas import gerar_etiquetas
import re

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def limpar_nome_escola_simples(nome):
    """Função SUPER SIMPLES para limpar nomes - SEM PERDER ESCOLAS"""
    if pd.isna(nome):
        return nome
    
    nome = str(nome).upper().strip()
    
    # Remove códigos INEP em qualquer formato: (INEP: 123), (INEP 123), INEP: 123, INEP 123
    nome = re.sub(r"\(?\bINEP:?\s*\d+\)?", "", nome).strip()
    
    # Lista simples de substituições - apenas remove do início
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
        "ESC MUN ",
        "E I F ",
        "E F ",
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
    """Detecta automaticamente as colunas da planilha e cria mapeamento dinâmico"""
    
    # Coluna obrigatória (nome da escola)
    coluna_escola = None
    for col in df.columns:
        if 'escola' in col.lower():
            coluna_escola = col
            break
    
    if not coluna_escola:
        return None, "Coluna com nome da escola não encontrada!"
    
    # Detectar colunas de alunos automaticamente
    colunas_alunos = []
    for col in df.columns:
        col_lower = col.lower()
        # Procura por padrões como "total", "aluno", números, "manhã", "tarde", "eja", etc.
        if any(palavra in col_lower for palavra in ['total', 'aluno', '1º', '2º', '3º', '4º', '5º', 
                                                    '6º', '7º', '8º', '9º', 'eja', 'manhã', 'tarde']):
            if col != coluna_escola:  # Não incluir a coluna da escola
                colunas_alunos.append(col)
    
    # Criar mapeamento dinâmico
    mapeamento = {coluna_escola: 'NOME ESCOLA'}
    
    # Para cada coluna de alunos, criar um nome mais limpo
    for col in colunas_alunos:
        nome_limpo = col.replace('Total de alunos do ', '').replace('Total de alunos da ', '')
        nome_limpo = nome_limpo.replace('Total de alunos ', '')  # cobre "Total de alunos EJAI 1"
        nome_limpo = nome_limpo.replace(' da ', ' ').replace(' do ', ' ')
        nome_limpo = nome_limpo.upper().strip()
        mapeamento[col] = nome_limpo
    
    return mapeamento, None

def ajustar_nome_ano_escolar(ano_escolar):
    """Ajusta nomes dos anos escolares:
    - EJAI + número → 'EJA 1', 'EJA 2', etc.
    - EJA (sem I) → mantém como está
    - Anos normais → mantém como está
    """
    if pd.isna(ano_escolar):
        return ano_escolar
        
    ano_str = str(ano_escolar).upper().strip()
    
    # EJAI com número → formatar como "EJA 1", "EJA 2", etc.
    if 'EJAI' in ano_str:
        match = re.search(r'\d+', ano_str)
        if match:
            return f"EJAI {match.group()}"
        return ano_str  # fallback se não tiver número
    
    # EJA sem I: manter como está
    elif 'EJA' in ano_str:
        return ano_str
    
    # Anos normais: manter como está
    else:
        return ano_str

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
        "Total de alunos da EJA 1ª ETAPA",
        "Total de alunos da EJA 2ª ETAPA",
        "Total de alunos da EJA 3ª ETAPA", 
        "Total de alunos da EJA 4ª ETAPA",
        "Total de alunos EJAI 1",
        "Total de alunos EJAI 2",
        "Total de alunos EJAI 3",
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
        "Total de alunos do 1º ano da TARDE": [20],
        "Total de alunos do 2º ano da MANHÃ": [30],
        "Total de alunos do 2º ano da TARDE": [28],
    }
    st.markdown("### 📊 Estrutura esperada da planilha:")
    st.dataframe(pd.DataFrame(exemplo))

    uploaded_file = st.file_uploader("Carregar planilha CSV", type="csv")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Detectar colunas automaticamente
            mapeamento, erro = detectar_colunas_automaticamente(df)
            
            if erro:
                st.error(f"❌ {erro}")
                st.info("Verifique se existe uma coluna com 'escola' no nome")
                st.stop()
            
            # Aplicar mapeamento
            df_mapeado = df.rename(columns=mapeamento)
            colunas_finais = list(mapeamento.values())
            df_final = df_mapeado[colunas_finais].copy()
            
            # Transformar para formato longo
            colunas_anos = [col for col in colunas_finais if col != 'NOME ESCOLA']
            if not colunas_anos:
                st.warning("Nenhuma coluna de alunos foi detectada!")
                st.stop()
                
            df_transformado = df_final.melt(
                id_vars=['NOME ESCOLA'], 
                value_vars=colunas_anos,
                var_name='ANO ESCOLAR', 
                value_name='TOTAL'
            )
            
            # Limpeza cuidadosa dos dados
            df_transformado = df_transformado.dropna(subset=['NOME ESCOLA'])
            df_transformado['TOTAL'] = pd.to_numeric(df_transformado['TOTAL'], errors='coerce').fillna(0).astype(int)
            
            # Estratégia para NÃO perder escolas:
            # 1. Manter todas as linhas com TOTAL > 0
            linhas_com_alunos = df_transformado[df_transformado['TOTAL'] > 0].copy()
            
            # 2. Para escolas que só têm TOTAL = 0, manter pelo menos uma linha
            escolas_com_alunos = linhas_com_alunos['NOME ESCOLA'].unique()
            escolas_sem_alunos = df_transformado[~df_transformado['NOME ESCOLA'].isin(escolas_com_alunos)]
            
            if not escolas_sem_alunos.empty:
                # Manter uma linha por escola que só tem zeros
                linhas_sem_alunos = escolas_sem_alunos.groupby('NOME ESCOLA').first().reset_index()
                df_final_processado = pd.concat([linhas_com_alunos, linhas_sem_alunos], ignore_index=True)
            else:
                df_final_processado = linhas_com_alunos.copy()
            
            if df_final_processado.empty:
                st.warning("⚠️ Não há dados válidos na planilha!")
                st.stop()

            # Aplicar limpeza automática dos nomes das escolas (sempre ativa)
            df_final_processado['NOME ESCOLA'] = df_final_processado['NOME ESCOLA'].apply(limpar_nome_escola_simples)
            
            # Ajustar nomes dos anos escolares
            df_final_processado['ANO ESCOLAR'] = df_final_processado['ANO ESCOLAR'].apply(ajustar_nome_ano_escolar)
                
            df_final_processado = df_final_processado.sort_values('NOME ESCOLA').reset_index(drop=True)

            # Resumo final
            st.markdown("### 📊 Resumo dos Dados Finais:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏫 Escolas", df_final_processado['NOME ESCOLA'].nunique())
            with col2:
                st.metric("📚 Turmas/Anos", df_final_processado['ANO ESCOLAR'].nunique())
            with col3:
                st.metric("👥 Total Alunos", df_final_processado['TOTAL'].sum())

            # Mostrar dados processados
            st.markdown("### 📋 Dados Processados:")
            st.dataframe(df_final_processado, use_container_width=True, hide_index=True)

            st.download_button(
                "📥 Baixar Planilha Tratada", 
                convert_df(df_final_processado), 
                "dados_processados.csv", 
                "text/csv"
            )

            # Gerar PDF das etiquetas
            st.markdown("### 🏷️ Gerar Etiquetas PDF")
            logo_file = st.file_uploader("Carregar logo (JPEG)", type=["jpg", "jpeg"])
            championship = st.text_input("Nome do Campeonato/Prova").upper()
            stage = st.text_input("Etapa/Fase").upper()

            if logo_file and championship and stage:
                try:
                    pdf_data = gerar_etiquetas(df_final_processado, logo_file, championship, stage)
                    st.download_button(
                        "📥 Baixar PDF das Etiquetas",
                        data=pdf_data,
                        file_name='etiquetas.pdf',
                        mime='application/pdf'
                    )
                    st.success("PDF gerado com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar planilha: {str(e)}")
            st.info("💡 Verifique se o arquivo CSV está no formato correto.")