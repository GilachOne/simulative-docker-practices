# Docker Containers

Приложение умеет завершаться после приветствия или оставаться запущенным с --wait. Проверены запуск run, отдельные create/start, logs, exec, cp, inspect, diff, top, stats, pause/unpause, restart, stop/start, rename и rm. Полная последовательность и вывод находятся в evidence/verification.txt.

```sh
docker build -t gilachone/simulative-practice-containers:1.0 .
docker run -d --name practice-run gilachone/simulative-practice-containers:1.0 --wait
docker logs practice-run
docker exec practice-run python -c "print('exec works')"
docker restart practice-run
docker stop practice-run
docker start practice-run
docker rm -f practice-run
docker create --name practice-created gilachone/simulative-practice-containers:1.0 --name Created
docker start -a practice-created
docker rm practice-created
```

Команды удаления выше относятся только к созданным здесь тестовым контейнерам. Образ после удаления контейнера остается доступным.

Образ: https://hub.docker.com/r/gilachone/simulative-practice-containers
