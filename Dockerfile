FROM python:3.8.3-alpine3.12

WORKDIR /app

COPY AppInsightsExporterApp/requirements.txt ./

RUN pip install -r requirements.txt


COPY AppInsightsExporterApp /app


ENTRYPOINT ["python", "AppInsightsExporter.py"]