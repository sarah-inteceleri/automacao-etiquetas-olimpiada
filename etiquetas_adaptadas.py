import streamlit as st
import pandas as pd
from criacao_adaptadas import gerar_etiquetas

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

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
    st.dataframe(pd.DataFrame(exemplo))

    uploaded_file = st.file_uploader("Carregue sua planilha (CSV ou Excel)", type=['csv', 'xlsx'])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = [col.upper() for col in df.columns]
        df = df.rename(columns={'ESCOLA': 'NOME ESCOLA', 'ANO': 'ANO ESCOLAR'})
        df['ANO ESCOLAR'] = df['ANO ESCOLAR'].astype(str).str.strip()
        df.loc[~df['ANO ESCOLAR'].str.upper().str.contains("EJAI"), 'ANO ESCOLAR'] += " ANO"

        st.subheader("Dados Originais")
        st.dataframe(df)

        col_qtd = [c for c in df.columns if df[c].dtype in ['int64', 'float64']]
        if col_qtd:
            df_transformado = df[df[col_qtd[0]] > 0]
        else:
            df_transformado = df.copy()

        st.subheader("Dados Transformados")
        st.dataframe(df_transformado)

        st.download_button("Baixar arquivo transformado (CSV)", convert_df(df_transformado), "dados_transformados.csv", "text/csv")

        logo_file = st.file_uploader("Carregue a imagem da logo para o PDF", type=["png", "jpg", "jpeg"])
        campeonato = st.text_input("Nome do Campeonato").upper()
        etapa = st.text_input("Etapa").upper()

        if logo_file and campeonato and etapa:
            st.download_button(
                label="Baixar PDF de Etiquetas",
                data=gerar_etiquetas(df_transformado, logo_file, campeonato, etapa),
                file_name='etiquetas_adaptadas.pdf',
                mime='application/pdf'
            )
