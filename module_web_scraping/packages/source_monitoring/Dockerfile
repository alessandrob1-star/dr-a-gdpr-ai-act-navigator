FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY module_web_scraping/packages/source_monitoring/README.md ./README.md
COPY module_web_scraping/packages/source_monitoring/package_manifest.yml ./package_manifest.yml
COPY module_web_scraping/packages/source_monitoring/smoke.py ./smoke.py
COPY module_web_scraping/packages/source_monitoring/requirements.txt ./requirements.txt
COPY module_web_scraping ./module_web_scraping
COPY data ./data

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "smoke.py"]
