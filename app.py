import json
import os
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_extras.metric_cards import style_metric_cards
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from jira_utils import JiraIssue, download_jira_issues

########## Variáveis
CUSTOM_COLORS = {'Pronto': '#9FC131', 'Em andamento': '#042940', 'Aberto': '#005C53'}

########## Configurações de estilo
def st_metric_cards(
        color:str = "#232323",
        background_color: str = "#FFF",
        border_size_px: int = 1,
        border_color: str = "#CCC",
        border_radius_px: int = 5,
        border_left_color: str = "#9AD8E1",
        box_shadow: bool = True,
    ):

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="stMetric"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 5% 5% 10%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                color: {color}; 
                {box_shadow_str}
            }}
             div[data-testid="stMetric"] p {{
              color: {color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

########## Dialog
@st.experimental_dialog("Download das issues do Jira")
def download():
    jira_url = st.text_input("URL do Jira", value='https://zerumbr.atlassian.net')
    username = st.text_input("Usuário", '')
    password = st.text_input("Auth Token", type="password", value='')
    max_results = st.number_input("Quantidade de resultados", value=100, help='0 significa todos os resultados')
    jql_query = st.text_input("JQL Query", value="project = 'DATA'")
    filename = st.text_input("Nome do arquivo")

    if st.button("Baixar issues"):
        if jira_url and username and password and jql_query:
            with st.spinner(text='Baixando arquivo JSON com issues...'):
                opts = (
                    jira_url, username, password, jql_query, max_results,
                    filename
                )
                download_jira_issues(*opts)
        else:
            st.error("Por favor, preencha todos os campos.")


########## MAIN

### Page config
st.set_page_config(
    page_title='Dashboard Jira',
    page_icon="📈",
    layout='wide',
)

### Componentes
sidebar = st.sidebar
container0 = st.container()
container1 = st.container()
container2 = st.container()
container3 = st.container()
container4 = st.container()
container5 = st.container()

with sidebar:
    def file_selector(folder_path='./data'):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox('Selecione um arquivo', [''] + filenames)
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()
    st.write('Arquivo selecionado`%s`' % filename)

    if "download" not in st.session_state:
        if st.button("Download das issues do Jira"):
            download()
 
if filename == './data/':
    st.info("Selecione um arquivo na barra lateral")
    st.stop()

with open(filename) as f:
    issues_raw = json.load(f)

issues = [JiraIssue(i) for i in issues_raw]

df = pd.DataFrame([i.as_dict() for i in issues])

df['dt_updated'] = df['dt_updated'].str.slice(stop=10)
df['dt_updated'] = pd.to_datetime(df['dt_updated'])

zerum_sprint = df['zerum_sprint'].dropna().unique().tolist()

with container0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.title('Data issues board')
        st.markdown("_v0.1.0_")
        
    with col3:
        selected_sprint = st.multiselect('Escolha uma sprint:', [''] + zerum_sprint)

if selected_sprint:
    df = df[df['zerum_sprint'].isin(selected_sprint)]


# Container com cards de métricas
with container1:

    col1, col2, col3, col4 = st.columns(4)
    
    # create column span
    col1.metric(label="Tarefas", value=df.count()['key'])
    
    col2.metric(label="Escopos", value= df['scope'].nunique())
    
    col3.metric(label="Categorias", value=df['category'].nunique())
    
    col4.metric(label="Total de pontos das histórias", value=int(np.round(df['story_points'].sum())))
    
    st_metric_cards(border_left_color="#DBF227")
    
    
# Container com a média de pontos nas histórias
with container2:
    
    col1,col2 = st.columns([1,2])
    
    with col1:
        value =int(np.round(df['story_points'].mean()))

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': "Média de pontos das histórias"},
            gauge={'axis': {'range': [df['story_points'].min() , df['story_points'].max()]},
                'bar': {'color': "#005C53"},
                }
        ))

        fig.update_layout(height=350) 

        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        
        grouping_scope_by_status = df.groupby(['scope','status']).size().reset_index(name='count')

        bars = alt.Chart(grouping_scope_by_status).mark_bar().encode(
            y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s') ),
            x=alt.X('scope:N'),
            color=alt.Color('status:N', scale=alt.Scale(domain=list(CUSTOM_COLORS.keys()), range=list(CUSTOM_COLORS.values())))
        )

        text = alt.Chart(grouping_scope_by_status).mark_text(dx=-15, dy=30, color='white').encode(
            y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s'), title='Contagem'),
            x=alt.X('scope:N', title='Escopo'),
            detail='status:N'
            # text=alt.Text('count:Q')
          )

        chart = bars + text

        chart = chart.properties(title="Quantidade de tarefas por Escopo e Status" )

        st.altair_chart(chart, use_container_width=True)
    
# Container com a média de pontos nas histórias
grouping_status = pd.DataFrame(df['status'].value_counts().reset_index())

with container3:
    
    col1,col2 = st.columns([1,2])
    
    with col1:
        grouping_status = pd.DataFrame(df['status'].value_counts().reset_index())

        fig = go.Figure(
            data = go.Pie(
                labels=grouping_status['status'], 
                values=grouping_status['count'],
                marker=dict(colors=[CUSTOM_COLORS[x] for x in grouping_status['status']]),
                hoverinfo='label+value',
                textinfo='label+percent',
                textfont=dict(size=13),
                hole=.4,
                rotation=45,
                pull=[.025] * len(grouping_status['status'])
                ),
            layout=go.Layout(
                hovermode='closest',
                title={
                    'text': 'Status das atividades'
                    # 'yanchor': 'top'
                    },
                legend={
                    'orientation': 'h',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.07},
                font=dict(
                    family="sans-serif",
                    size=12,
                    color='white')
                )
            )

        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        
        grouping_category_by_status = df.groupby(['category','status']).size().reset_index(name='count')

        bars = alt.Chart(grouping_category_by_status).mark_bar().encode(
            y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s') ),
            x=alt.X('category:N'),
            color=alt.Color('status:N', scale=alt.Scale(domain=list(CUSTOM_COLORS.keys()), range=list(CUSTOM_COLORS.values())))
        )

        text = alt.Chart(grouping_category_by_status).mark_text(dx=-15, dy=30, color='white').encode(
            y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s'), title='Contagem'),
            x=alt.X('category:N', title='Categoria'),
            detail='status:N'
            # text=alt.Text('count:Q')
          )

        chart = bars + text

        chart = chart.properties(title="Quantidade de tarefas por Categoria e Status" )

        st.altair_chart(chart, use_container_width=True)
    
with container4:
    grouping_date_by_status = df.groupby(['dt_updated','status']).size().reset_index(name='count')

    fig = px.bar(
        grouping_date_by_status, 
        x="dt_updated", 
        y="count", 
        color="status", 
        title="Status das atividades no período",
        color_discrete_map=CUSTOM_COLORS,
        labels={
            'dt_updated': '', 
            'count':'Contagem',
            'status': 'Status'
            }
        )

    st.plotly_chart(fig, use_container_width=True)
    
with container5:
    with st.expander('Dados dos itens'):
        st.dataframe(df)

print('--')