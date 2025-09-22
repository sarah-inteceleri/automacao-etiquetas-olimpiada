import streamlit as st
import pandas as pd
from etiquetas_nao_adaptadas import interface_nao_adaptadas
from etiquetas_adaptadas import interface_adaptadas

st.set_page_config(page_title="Etiquetas de Provas", layout="wide")

# --- MENU ---
st.sidebar.title("Menu")
opcao = st.sidebar.radio("Escolha o tipo de etiqueta:", ["Provas Não Adaptadas", "Provas Adaptadas"])

st.sidebar.markdown("---")
st.sidebar.info(
    "⚠️ Observação: É importante ressaltar que os dados de quantitativo de alunos "
    "devem estar formatados como números. Para isso, no Google Planilhas selecione os dados "
    "e vá até **Formatar → Número → Formato de número personalizado**."
)

# --- INTERFACE ---
if opcao == "Provas Não Adaptadas":
    interface_nao_adaptadas()

elif opcao == "Provas Adaptadas":
    interface_adaptadas()

