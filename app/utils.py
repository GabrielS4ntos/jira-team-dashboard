import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import altair as alt

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


########## Parameters to download issues in a JSON file
def download():
    jira_url = st.secrets['JIRA_BASE_URL']
    username = st.secrets['JIRA_EMAIL']
    password = st.secrets['API_TOKEN']
    max_results = 100
    jql_query = "project = 'DATA'"

    with st.spinner(text='Baixando arquivo JSON com issues...'):
        opts = (
            jira_url, username, password, jql_query, max_results
        )
        download_jira_issues(*opts)
    
########## Transformando variáveis de data
def date_convert(data, vars):
    for var in vars:
        data[var] = data[var].str.slice(stop=10)
        data[var] = pd.to_datetime(data[var])
        
    return data

########## Gerando data frame
def generate_dataframe():
    ## Faz o download das issues caso ainda não tenha sido feito
    if "download" not in st.session_state:
        download()
        st.session_state['download'] = True

    filename = os.path.join('./data/jiratasks')

    with open(filename) as f: 
        issues_raw = json.load(f)

    issues = [JiraIssue(i) for i in issues_raw]

    df = pd.DataFrame([i.as_dict() for i in issues])

    df = date_convert(df, ['dt_updated', 'start_sprint'])
    
    return df

########## CHARTS

## indicator
def indicator_plot(data):
    value =int(np.round(data['story_points'].mean()))

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Média de pontos das histórias"},
        gauge={'axis': {'range': [data['story_points'].min() , data['story_points'].max()]},
            'bar': {'color': "#005C53"},
            }
    ))

    fig.update_layout(height=350) 

    return st.plotly_chart(fig, use_container_width=True)

## gráfico de agrupamento
def grouping_plot(data, xvar, yvar, title):
    
    grouping_data = data.groupby([xvar, yvar]).size().reset_index(name='count')

    bars = alt.Chart(grouping_data).mark_bar().encode(
        y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s') ),
        x=alt.X(xvar+':N'),
        color=alt.Color(yvar+':N', scale=alt.Scale(domain=list(CUSTOM_COLORS.keys()), range=list(CUSTOM_COLORS.values())))
    )

    text = alt.Chart(grouping_data).mark_text(dx=-15, dy=30, color='white').encode(
        y=alt.Y('count:Q', stack='zero', axis=alt.Axis(format='~s'), title='Contagem'),
        x=alt.X(xvar+':N', title='Sprint'),
        detail=yvar+':N',
        
        )

    chart = bars + text

    chart = chart.properties(title=title)

    return st.altair_chart(chart, use_container_width=True)

def donuts_plot(data):
    
    grouping_status = pd.DataFrame(data['status'].value_counts().reset_index())

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

    return st.plotly_chart(fig, use_container_width=True)

def grouping_for_date(data, datefield):
    grouping_data = data.groupby([datefield,'status']).size().reset_index(name='count')

    fig = px.bar(
        grouping_data, 
        x=datefield, 
        y="count", 
        color="status", 
        title="Status das atividades no período",
        color_discrete_map=CUSTOM_COLORS,
        labels={
            datefield: '', 
            'count':'Contagem',
            'status': 'Status'
            }
        )

    return st.plotly_chart(fig, use_container_width=True)