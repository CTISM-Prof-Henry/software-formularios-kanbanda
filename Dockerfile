FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/CTISM-Prof-Henry/software-formularios-kanbanda.git .

RUN pip install --no-cache-dir -r requirements.txt

RUN python risco_ufsm/manage.py collectstatic --no-input

RUN mkdir -p /app/logs

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python risco_ufsm/manage.py migrate && python risco_ufsm/manage.py runserver 0.0.0.0:8000 >> /app/logs/django.log 2>&1"]