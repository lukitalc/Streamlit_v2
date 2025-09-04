import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard de Telecom Brasília", layout="wide")

# --- Dados de Referência: 35 RAs de Brasília com coordenadas fictícias ---
# NOTA: As coordenadas são aproximadas e fictícias para fins de demonstração
ras_data = {
    'RA': [
        'Plano Piloto', 'Gama', 'Taguatinga', 'Brazlândia', 'Sobradinho', 'Planaltina',
        'Paranoá', 'Núcleo Bandeirante', 'Ceilândia', 'Guará', 'Cruzeiro', 'Samambaia',
        'Santa Maria', 'São Sebastião', 'Recanto das Emas', 'Lago Sul', 'Riacho Fundo',
        'Lago Norte', 'Candangolândia', 'Águas Claras', 'Riacho Fundo II', 'Sudoeste/Octogonal',
        'Varjão', 'Park Way', 'SCIA', 'Sobradinho II', 'Jardim Botânico', 'Itapoã',
        'SIA', 'Vicente Pires', 'Fercal', 'Arniqueira', 'Sol Nascente/Pôr do Sol',
        'Arapoanga', 'Ribeirão do Pires'
    ],
    'lat': [
        -15.7942, -16.0125, -15.8273, -15.7001, -15.6565, -15.6133, -15.7834, -15.8647,
        -15.8118, -15.8239, -15.7877, -15.8660, -16.0118, -15.9329, -15.8929, -15.8427,
        -15.9221, -15.7483, -15.8851, -15.8368, -15.9080, -15.7997, -15.7277, -15.9048,
        -15.7925, -15.5861, -15.8507, -15.7018, -15.7942, -15.8184, -15.6027, -15.8491,
        -15.7900, -15.6745, -15.9500
    ],
    'lon': [
        -47.8822, -48.0673, -48.0519, -48.0838, -47.8284, -47.6049, -47.7818, -47.9940,
        -48.1068, -47.9427, -47.9157, -48.1189, -48.0121, -47.8596, -48.1122, -47.8680,
        -48.0658, -47.8239, -47.9402, -48.0673, -48.0069, -47.9304, -47.8690, -47.9545,
        -47.9500, -47.8000, -47.8384, -47.7479, -47.9500, -48.0594, -47.9520, -48.0500,
        -48.1400, -47.7400, -47.8200
    ]
}
df_ras = pd.DataFrame(ras_data)

# --- Simulação de Dados de Ordens de Serviço ---
np.random.seed(42)
num_os = 500
status = ['Concluída', 'Em Andamento', 'Aberta', 'Cancelada']
tipos_servico = ['Instalação', 'Reparo', 'Manutenção']

df_os = pd.DataFrame({
    'id_os': range(1, num_os + 1),
    'status': np.random.choice(status, num_os),
    'tipo_servico': np.random.choice(tipos_servico, num_os),
    'ra': np.random.choice(df_ras['RA'], num_os),
    'prioridade': np.random.choice(['Alta', 'Média', 'Baixa'], num_os),
    'tempo_abertura_dias': np.random.randint(1, 10, num_os)
})

# Mescla os dados das OS com as coordenadas das RAs
df_os_full = pd.merge(df_os, df_ras, left_on='ra', right_on='RA')

# Mapeamento de cores para os status
status_colors = {
    'Aberta': 'red',
    'Em Andamento': 'orange',
    'Concluída': 'green',
    'Cancelada': 'grey'
}

# --- Título do Dashboard ---
st.title("Telemetria do Controle de Operações - Brasília")
st.markdown("---")

# --- Barra Lateral de Filtro ---
st.sidebar.header("Filtros")
status_filtro = st.sidebar.multiselect(
    'Filtrar por Status',
    options=df_os_full['status'].unique(),
    default=df_os_full['status'].unique()
)
df_filtrado = df_os_full[df_os_full['status'].isin(status_filtro)]

# --- Métricas de Alto Nível (KPIs) ---
st.subheader("Resumo de Produtividade")
col1, col2, col3, col4 = st.columns(4)

total_os = len(df_filtrado)
abertas = len(df_filtrado[df_filtrado['status'] == 'Aberta'])
em_andamento = len(df_filtrado[df_filtrado['status'] == 'Em Andamento'])
concluidas = len(df_filtrado[df_filtrado['status'] == 'Concluída'])

with col1:
    st.metric("Total de OS", total_os)
with col2:
    st.metric("OS Abertas", abertas)
with col3:
    st.metric("OS Em Andamento", em_andamento)
with col4:
    st.metric("OS Concluídas", concluidas)

st.markdown("---")

# --- Gráfico de Mapa com Plotly ---
st.subheader("Visualização de Ordens de Serviço por Região Administrativa")

# Criação do mapa com Plotly Express
fig_mapa = px.scatter_mapbox(
    df_filtrado, 
    lat="lat", 
    lon="lon", 
    color="status",
    color_discrete_map=status_colors,
    hover_name="ra",
    hover_data={'tipo_servico': True, 'prioridade': True, 'lat': False, 'lon': False},
    zoom=9, 
    height=500
)

# Adiciona o estilo de mapa de satélite
fig_mapa.update_layout(
    mapbox_style="open-street-map",  # Você pode usar "satellite-streets" se tiver uma chave Mapbox
    mapbox_center={"lat": -15.7942, "lon": -47.8822},
    margin={"r":0, "t":0, "l":0, "b":0}
)

st.plotly_chart(fig_mapa, use_container_width=True)

# --- Gráficos de Distribuição ---
st.markdown("---")
st.subheader("Análise Gráfica das Ordens de Serviço")
row1_col1, row1_col2 = st.columns(2)

# Gráfico de barras: Status das OS
with row1_col1:
    status_counts = df_filtrado['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'contagem']
    fig_status = px.bar(
        status_counts,
        x='status',
        y='contagem',
        title='Distribuição de OS por Status',
        color='status',
        color_discrete_map=status_colors
    )
    st.plotly_chart(fig_status, use_container_width=True)

# Gráfico de pizza: Tipos de Serviço
with row1_col2:
    tipo_servico_counts = df_filtrado['tipo_servico'].value_counts().reset_index()
    tipo_servico_counts.columns = ['tipo_servico', 'contagem']
    fig_tipo = px.pie(
        tipo_servico_counts,
        names='tipo_servico',
        values='contagem',
        title='Proporção de OS por Tipo de Serviço'
    )
    st.plotly_chart(fig_tipo, use_container_width=True)

# --- Tabela Detalhada ---
st.markdown("---")
st.subheader("Detalhes das Ordens de Serviço")
st.dataframe(df_filtrado)
