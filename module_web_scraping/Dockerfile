FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY module_web_scraping ./module_web_scraping
COPY data ./data
COPY config ./config

RUN mkdir -p storage

ENTRYPOINT ["python", "-m", "module_web_scraping.cli"]
CMD ["seed-dashboard"]
