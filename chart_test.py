from jira_utils import JiraIssue, download_jira_issues
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "vscode"


def _get_attr(path, raw):
    res = raw
    for subpath in path.split('.'):
        if res:
            # Corrigindo erro de quando aparece uma lista com 1 resultado
            if type(res) == list:
                # res = res
                res = res[0].get(subpath, None)
            else:
                res = res.get(subpath, None)
                
    return res

with open('./data/teste4') as f:
    issues_raw = json.load(f)

# for i in issues_raw:
#     print(_get_attr('fields.status.name', i))
#     print(_get_attr('fields.created', i))
#     print(_get_attr('fields.updated', i))
#     break
    # print(_get_attr('fields.customfield_10027', i))

issues = [JiraIssue(i) for i in issues_raw]

df = pd.DataFrame([i.as_dict() for i in issues])
df['dt_updated'] = df['dt_updated'].str.slice(stop=10)
df['dt_updated'] = pd.to_datetime(df['dt_updated'])
print(df.dtypes)
# print(df.head())

# table_status = pd.DataFrame(df['status'].value_counts().reset_index())
# print(list(table_status['status']))
 
# fig = go.Pie(
#     labels=table_status['status'],
#     values=table_status['count'],
#     marker=dict(colors=['#005C53', '#9FC131']),
#     hoverinfo='label+value+percent',
#     textinfo='label+value',
#     textfont=dict(size=13),
#     hole=.7,
#     rotation=45
#     # insidetextorientation='radial',
#     )

# fig.show()

