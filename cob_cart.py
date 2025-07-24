import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO


st.set_page_config(
    page_title="Dashboard Analítico",
    page_icon="https://raw.githubusercontent.com/carlinhosg7/cob_cart/refs/heads/main/logo_kidy_icon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Análise de Cobertura de Carteira por Representante")

# ✅ URL RAW correta do GitHub
URL_DADOS = "https://raw.githubusercontent.com/carlinhosg7/cob_cart/main/Cobertura_de_Carteira.xlsx"

try:
    # Baixa o conteúdo do Excel da URL
    response = requests.get(URL_DADOS)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content), header=7, engine="openpyxl")
    df.columns = df.columns.str.strip()
    
    # Lê a aba de meta
    df_meta = pd.read_excel(BytesIO(response.content), sheet_name='% cOB. caRT', engine="openpyxl")
    cobertura_ideal = df_meta.iloc[7, 3]
    cobertura_ideal_fmt = f"{cobertura_ideal * 100:.1f}%"

    colunas_ok = ['Rep', 'Nome Rep.', 'Saldo de Carteira', 'cobertura']
    if all(col in df.columns for col in colunas_ok):
        df = df.dropna(subset=['Rep', 'Saldo de Carteira', 'cobertura'])
        df = df.sort_values(by='Saldo de Carteira', ascending=False)

        # ➕ Calcula o % de cobertura por representante
        df['% Cobertura'] = df.apply(
            lambda row: (row['cobertura'] / row['Saldo de Carteira']) * 100 if row['Saldo de Carteira'] != 0 else 0,
            axis=1
        )
        df['% Cobertura'] = df['% Cobertura'].round(1)

        # 🔁 FILTROS AGRUPADOS EM EXPANDER
        with st.expander("🎯 Filtros de Seleção", expanded=True):
            if 'Supervisor' in df.columns:
                supervisores_disponiveis = sorted(df['Supervisor'].dropna().unique().tolist())
                supervisores_selecionados = st.multiselect(
                    "🧑‍💼 Selecione o(s) Supervisor(es):",
                    options=supervisores_disponiveis,
                    default=supervisores_disponiveis
                )
                st.caption(f"✅ {len(supervisores_selecionados)} supervisor(es) selecionado(s)")
                if supervisores_selecionados:
                    df = df[df['Supervisor'].isin(supervisores_selecionados)]

            reps_disponiveis = sorted(df['Rep'].unique().tolist())
            reps_selecionados = st.multiselect(
                "👤 Selecione o(s) Representante(s):",
                options=reps_disponiveis,
                default=reps_disponiveis
            )
            st.caption(f"✅ {len(reps_selecionados)} representante(s) selecionado(s)")
            if reps_selecionados:
                df = df[df['Rep'].isin(reps_selecionados)]

        total_saldo = df['Saldo de Carteira'].sum()
        total_cobertura = df['cobertura'].sum()
        perc_total = round((total_cobertura / total_saldo) * 100, 1)

        st.markdown("### 📉 Evolução da Carteira x Cobertura")
        fig_linha = go.Figure()

        fig_linha.add_trace(go.Scatter(
            x=df['Rep'].astype(str),
            y=df['Saldo de Carteira'],
            mode='lines+markers+text',
            name='💼 Carteira',
            line=dict(color='lightgray', width=3),
            marker=dict(size=6),
            text=df['Saldo de Carteira'].round(0).astype(int),
            textposition='top right',
            textfont=dict(size=10)
        ))

        fig_linha.add_trace(go.Scatter(
            x=df['Rep'].astype(str),
            y=df['cobertura'],
            mode='lines+markers+text',
            name='✅ Cobertura',
            line=dict(color='#FF6600', width=3),
            marker=dict(size=6),
            text=df['cobertura'].round(0).astype(int),
            textposition='bottom right',
            textfont=dict(size=10)
        ))

        fig_linha.update_layout(
            xaxis_title='Representante',
            yaxis_title='Clientes',
            legend_title='Indicador',
            height=450,
            template='plotly_white',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_linha, use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(y=["TOTAL"], x=[total_saldo], name='Saldo de Carteira', orientation='h', marker=dict(color='lightgray')))
        fig.add_trace(go.Bar(y=["TOTAL"], x=[total_cobertura], name='Cobertura', orientation='h', marker=dict(color='#FF6600')))
        fig.update_layout(barmode='overlay', title='Cobertura Total da Carteira', xaxis_title='Número de Clientes', yaxis_title='', height=300,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st.markdown("### 📊 Resumo da Cobertura")
            col1, col2, col3, col4 = st.columns(4)
            estilo = """
                <div style='
                    border: 2px solid #ddd;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                '>
                    <div style='font-size: 20px; font-weight: bold;'>{}</div>
                    <div style='font-size: 32px; color: #444; margin-top: 8px;'>{}</div>
                </div>
            """
            col1.markdown(estilo.format("💼 Carteira", f"{total_saldo:,.0f}".replace(",", ".")), unsafe_allow_html=True)
            col2.markdown(estilo.format("✅ Cobertura", f"{total_cobertura:,.0f}".replace(",", ".")), unsafe_allow_html=True)
            col3.markdown(estilo.format("📈 % Cobertura", f"{perc_total:.1f}%"), unsafe_allow_html=True)
            col4.markdown(estilo.format("🎯 Deveríamos Estar em:", cobertura_ideal_fmt), unsafe_allow_html=True)

        st.subheader("📋 Cobertura Geral (%)")
        st.dataframe(df[['Rep', 'Nome Rep.', 'Saldo de Carteira', 'cobertura', '% Cobertura']])

    else:
        # 👤 Visualização individual por representante
        rep_selecionado = st.selectbox("Selecione um representante:", df['Rep'].unique())
        df_filtrado = df[df['Rep'] == rep_selecionado]
        total_saldo = df_filtrado['Saldo de Carteira'].sum()
        total_cobertura = df_filtrado['cobertura'].sum()

        df_filtrado['% Cobertura'] = df_filtrado.apply(
            lambda row: (row['cobertura'] / row['Saldo de Carteira']) * 100 if row['Saldo de Carteira'] != 0 else 0,
            axis=1
        )
        df_filtrado['% Cobertura'] = df_filtrado['% Cobertura'].round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_filtrado['Rep'].astype(str),
            x=df_filtrado['Saldo de Carteira'],
            name='Saldo de Carteira',
            orientation='h',
            marker=dict(color='lightgray')
        ))
        fig.add_trace(go.Bar(
            y=df_filtrado['Rep'].astype(str),
            x=df_filtrado['cobertura'],
            name='Cobertura',
            orientation='h',
            marker=dict(color='#FF6600')
        ))
        fig.update_layout(
            barmode='overlay',
            title=f'Cobertura de Carteira - Rep {rep_selecionado}',
            xaxis_title='Número de Clientes',
            yaxis_title='Representante',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("💼 Carteira", f"{total_saldo:,.0f}".replace(",", "."), help="Total de clientes ativos")
        col2.metric("✅ Cobertura", f"{total_cobertura:,.0f}".replace(",", "."), help="Clientes já positivados")

        st.subheader("📋 Detalhamento da Cobertura (%)")
        st.dataframe(df_filtrado[['Rep', 'Nome Rep.', 'Saldo de Carteira', 'cobertura', '% Cobertura']])

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados do GitHub: {e}")

