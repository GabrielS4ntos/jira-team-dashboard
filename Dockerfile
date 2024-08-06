FROM python:3.11-slim

WORKDIR /usr/src/app

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Environment variables for JIRA
ENV JIRA_BASE_URL=https://your-domain.atlassian.net
ENV JIRA_EMAIL=your-email@example.com
ENV JIRA_API_TOKEN=your-api-token

COPY ./requirements.txt /usr/src/app/requirements.txt

# dependencies
RUN pip install --upgrade pip setuptools wheel \
  && pip install -r requirements.txt \
  && rm -rf /root/.cache/pip

COPY ./app /usr/src/app

ENTRYPOINT ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"]