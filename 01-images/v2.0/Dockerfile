FROM python:3.12-slim
WORKDIR /app
COPY message.txt .
CMD ["python", "-c", "from pathlib import Path; print(Path('message.txt').read_text().strip())"]
