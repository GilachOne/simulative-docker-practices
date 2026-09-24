# Dockerfile

Python-приложение печатает приветствие и версию.

```sh
docker build --build-arg APP_VERSION=1.0 -t gilachone/simulative-practice-dockerfile:1.0 .
docker run --rm gilachone/simulative-practice-dockerfile:1.0
docker run --rm gilachone/simulative-practice-dockerfile:1.0 --name Analyst
docker run --rm -e APP_NAME=Environment gilachone/simulative-practice-dockerfile:1.0 --wait
```

Последняя команда работает до Ctrl+C. ARG используется при сборке; его значение переносится в ENV для работы приложения и в LABEL для метаданных. ENTRYPOINT фиксирует Python и app.py; CMD задает аргументы по умолчанию. Аргументы после имени образа заменяют CMD. `--entrypoint` позволяет заменить саму команду запуска.

WORKDIR задает каталог, COPY копирует контекст, RUN проверяет синтаксис, USER запускает приложение без root. .dockerignore исключает тестовый ignored.txt, .env и служебные файлы; отсутствие ignored.txt внутри образа проверено отдельной командой.

Образ: https://hub.docker.com/r/gilachone/simulative-practice-dockerfile
