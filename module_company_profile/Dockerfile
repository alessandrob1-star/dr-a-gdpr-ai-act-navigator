FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY module_company_profile ./module_company_profile
COPY module_web_scraping ./module_web_scraping
COPY module_agents ./module_agents
COPY policy_agent ./policy_agent

RUN pip install --no-cache-dir -r /app/module_company_profile/requirements.txt

RUN mkdir -p /app/input /app/output

ENTRYPOINT ["python", "/app/module_company_profile/memory_agent/company_memory_agent.py"]
CMD ["/app/input/questionnaire_answers.json", "--out", "/app/output"]
