FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY orchestration ./orchestration
COPY docs ./docs
RUN mkdir -p data/raw data/processed reports
CMD ["python", "-m", "orchestration.flow"]
