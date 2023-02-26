FROM python:3.9-slim

WORKDIR /app

COPY pipeline/train/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /app/logs
VOLUME /app/mlflow
VOLUME /app/assets

COPY pipeline/train/*.py .
COPY assets /app/assets


ENTRYPOINT [ "python", "train.py"]