import streamlit as st
import numpy as np
import plotly.express as px

from utils import st_metric_cards, generate_dataframe, indicator_plot, grouping_plot, donuts_plot, grouping_for_date

########## Variáveis
CUSTOM_COLORS = {'Pronto': '#9FC131', 'Em andamento': '#042940', 'Aberto': '#005C53'}

## Configurações da página
st.set_page_config(
    page_title='Dashboard Jira',
    page_icon=f"📈",
    layout='wide',
)

## Componentes
container0 = st.container()
container1 = st.container()
container2 = st.container()
container3 = st.container()
container4 = st.container()
container5 = st.container()

## Salvando os dados no arquivo JSON e lendo como df
df = generate_dataframe()

zerum_sprint = df['zerum_sprint'].dropna().unique().tolist()

with container0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.title('Estatísticas da Sprint')
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
        indicator_plot(data=df)
        
    with col2:
        
        grouping_plot(
            data=df, 
            xvar='scope', 
            yvar='status', 
            title='Quantidade de tarefas por Escopo e Status'
            )


with container3:
    
    col1,col2 = st.columns([1,2])
    
    with col1:
        donuts_plot(data=df)
        
    with col2:
        
        grouping_plot(
            data=df, 
            xvar='category', 
            yvar='status', 
            title='Quantidade de tarefas por Categoria e Status'
            )
    
with container4:
    
    grouping_for_date(data=df, datefield='dt_updated')

    
with container5:
    with st.expander('Dados dos itens'):
        st.dataframe(df)

print('--')