FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY module_web_scraping/packages/regulatory_data_storage/README.md ./README.md
COPY module_web_scraping/packages/regulatory_data_storage/package_manifest.yml ./package_manifest.yml
COPY module_web_scraping/packages/regulatory_data_storage/smoke.py ./smoke.py
COPY module_web_scraping/packages/regulatory_data_storage/docs ./docs
COPY module_web_scraping/packages/regulatory_data_storage/requirements.txt ./requirements.txt
COPY module_web_scraping ./module_web_scraping
COPY data ./data

RUN pip install --no-cache-dir -r requirements.txt && mkdir -p storage

CMD ["python", "smoke.py"]
