import json
import streamlit as st

from datetime import datetime

from jira import JIRA


class JiraIssue():
    OPEN_STATUS = [
        'Aberto', 'Blocked', 'Backlog',
        'Tarefas pendentes', 'Priorizado', 'Preparado', 'Priorizadas',
        'Open Lower Issues', 'To Do'
    ]
    DOING_STATUS = [
        'Em Refinamento', 'Em Revisão', 'Missing Fix', 'Pronto para revisão',
        'Ready to Review', 'Validação', 'Rejeitada', 'Em análise',
        'Homologação', 'Em andamento', 'Em desenvolvimento', 'UNDER REVIEW',
        'In Progress'
    ]
    CLOSED_STATUS = ['Concluído', 'Cancelado', 'Pronto', 'UPDATE TESTCASE', 'Done']

    def __init__(self, raw: dict) -> None:
        self.raw = raw

        self.project = self._get_attr('fields.project.key')
        self.zerum_sprint = self._get_attr('fields.customfield_10020.name')
        self.issue_type = self._get_attr('fields.issuetype.name')
        self.story_points = self._get_attr('fields.customfield_10027')
        self.scope = self._get_attr('fields.customfield_10122.value')
        self.category = self._get_attr('fields.customfield_10123.value')
        self.dt_updated = self._get_attr('fields.updated')
        self.key = self._get_attr('key')

        self.setup_status()

    def print(self):
        print(json.dumps(self.raw, indent=2))

    def as_dict(self):
        d = self.__dict__.copy()
        d.pop('raw')
        return d

    def setup_status(self):
        status = self._get_attr('fields.status.name')

        if status in self.OPEN_STATUS:
            self.status = 'Aberto'
        elif status in self.DOING_STATUS:
            self.status = 'Em andamento'
        elif status in self.CLOSED_STATUS:
            self.status = 'Pronto'
        else:
            self.status = f'{status} - FIXME'
    
    def _get_attr(self, path: str):
        res = self.raw
        for subpath in path.split('.'):
            if res:
                # Corrigindo erro de quando aparece uma lista com 1 resultado
                if type(res) == list:
                    res = res[0].get(subpath, None)
                else:
                    res = res.get(subpath, None)
        return res

# Função para baixar as issues do Jira
def download_jira_issues(jira_url, username, password, jql_query, max_results, filename):
    try:
        # Conectar ao Jira
        jira = JIRA(server=jira_url, basic_auth=(username, password))
        
        # Buscar issues usando JQL
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        # Processar e salvar issues em JSON
        issues_list = []
        for issue in issues:
            issues_list.append(issue.raw)
        
        # Salvar issues em um arquivo JSON
        now = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
        fname = filename if filename else f'issues-{now}.json'
        with open(f'./data/{fname}', 'w', encoding='utf-8') as f:
            json.dump(issues_list, f, ensure_ascii=False, indent=4)
        
        st.success(f"Issues baixadas e salvas com sucesso em {fname}")
    except Exception as e:
        st.error(f"Erro ao baixar issues do Jira: {e}")
