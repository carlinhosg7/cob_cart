
import streamlit as st

# ✅ Configuração inicial com ícone local
st.set_page_config(
    page_title="Dashboard Analítico",
    page_icon="logo_kidy_icon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Teste de Ícone Personalizado")
st.write("Se você vê o ícone na aba do navegador, tá funcionando!")
