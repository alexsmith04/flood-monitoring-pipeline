FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#Default command - starts a celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--pool=solo"]