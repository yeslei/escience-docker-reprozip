FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gpu_metadata.csv gpu_price_history.csv ./
COPY src ./src
COPY README.md pyproject.toml main.py ./

ENV PYTHONPATH=/app/src

CMD ["python", "main.py"]
