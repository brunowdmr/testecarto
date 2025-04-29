# %%
import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------
# Dados simulados
# ------------------------

# Resultados por carteira
dados_resultados = {
    'agencia': [1001, 1001, 1002, 1003],
    'carteira': ['A', 'B', 'A', 'C'],
    'atingimento': [85.5, 91.0, 76.4, 102.3]
}
df_resultados = pd.DataFrame(dados_resultados)

# Clientes
dados_clientes = {
    'mci': [111111, 222222, 333333, 444444],
    'cartao_ativo': [-1, 0, -1, 0],
    'cartao_adicional': [-1, -1, 0, 0],
    'publico_alvo': [-1, -1, 0, 0],
    'endiv_concorrencia': [12000, 8000, 25000, 15000],
    'limite_disponivel': [-1, -1, 0, -1]
}
df_clientes = pd.DataFrame(dados_clientes)

# ------------------------
# Layout com abas
# ------------------------

aba1, aba2 = st.tabs(["📊 Atingimento por Carteira", "👤 Consulta por Cliente (MCI)"])

# ------------------------
# Aba 1 – Atingimento por Carteira
# ------------------------
with aba1:
    st.header("📊 Consulta de Atingimento por Agência e Carteira")

    ag_selected = st.selectbox("Selecione a Agência:", sorted(df_resultados['agencia'].unique()))
    cart_selected = st.selectbox("Selecione a Carteira:", sorted(df_resultados[df_resultados['agencia'] == ag_selected]['carteira'].unique()))

    filtro = (df_resultados['agencia'] == ag_selected) & (df_resultados['carteira'] == cart_selected)
    dado = df_resultados[filtro]

    if not dado.empty:
        valor = float(dado['atingimento'].values[0])

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            title={'text': "Atingimento (%)"},
            gauge={
                'axis': {'range': [0, 110]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range': [0, 90], 'color': "#ffa07a"},      # abaixo da meta
                    {'range': [90, 100], 'color': "#f0e68c"},    # dentro da meta
                    {'range': [100, 110], 'color': "#90ee90"}    # acima da meta
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados não encontrados para essa combinação.")

# ------------------------
# Aba 2 – Consulta por MCI
# ------------------------
with aba2:
    st.header("👤 Consulta de Informações do Cliente (MCI)")

    mci_input = st.number_input("Digite o código do cliente (MCI):", step=1)

    def sim_nao(valor):
        return "Sim" if valor == -1 else "Não"

    if st.button("🔍 Buscar Cliente"):
        cliente = df_clientes[df_clientes['mci'] == mci_input]

        if not cliente.empty:
            row = cliente.iloc[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Cartão Ativo", sim_nao(row['cartao_ativo']))
                st.metric("Público Alvo", sim_nao(row['publico_alvo']))

            with col2:
                st.metric("Cartão Adicional", sim_nao(row['cartao_adicional']))
                st.metric("Limite Disponível", sim_nao(row['limite_disponivel']))

            with col3:
                st.metric("Endiv. Concorrência", f"R$ {row['endiv_concorrencia']:,}")
        else:
            st.warning("Cliente não encontrado na base.")
