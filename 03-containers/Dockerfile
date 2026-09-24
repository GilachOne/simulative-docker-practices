FROM python:3.12-slim
ARG APP_VERSION=1.0
LABEL org.opencontainers.image.title="Python Docker practice" \
      org.opencontainers.image.version=$APP_VERSION
ENV APP_VERSION=$APP_VERSION APP_NAME=student PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN python -m py_compile app.py
USER 10001:10001
ENTRYPOINT ["python", "app.py"]
CMD ["--name", "student"]
