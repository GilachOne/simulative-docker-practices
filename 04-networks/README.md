# Docker Networks

Python создает таблицу users в PostgreSQL, записывает три учебные строки и выводит SELECT. Повторный запуск сохраняет три строки благодаря первичному ключу и UPSERT. Собственные Dockerfile находятся в python/ и postgres/.

```sh
export POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
export DB_PASSWORD=$POSTGRES_PASSWORD
docker network create practice-net
docker run -d --name practice-db --network practice-net -e POSTGRES_USER=practice -e POSTGRES_DB=practice -e POSTGRES_PASSWORD gilachone/simulative-practice-postgres:1.0
# Дождаться: docker exec practice-db pg_isready -U practice -d practice
docker run --rm --network practice-net -e DB_HOST=practice-db -e DB_PASSWORD gilachone/simulative-practice-networks:1.0
```

Ожидаемый SELECT: [[1, "Anna"], [2, "Boris"], [3, "Vera"]].

В evidence/verification.txt проверены два контейнера nicolaka/netshoot, ping по IP и имени, подключение/отключение сетей, две сети одновременно и переход между ними. В default bridge связь по IP работает, автоматического DNS имен контейнеров нет. В пользовательской bridge-сети работают IP и имена. Режим none оставляет loopback; host использует сеть хоста. Host и none уже встроены в Docker — дополнительные сети с такими драйверами создавать не нужно. Контейнер из none нельзя просто подключить к bridge: для изменения режима его пересоздают. Между двумя обычными bridge-сетями связь заблокирована; после подключения ко второй сети становится доступна.

Проверены также Python + PostgreSQL в одной сети (успех), в разных сетях и none (ожидаемая ошибка), а также host-клиент через временно опубликованный на localhost порт БД.

Образы:
- https://hub.docker.com/r/gilachone/simulative-practice-networks
- https://hub.docker.com/r/gilachone/simulative-practice-postgres

Документация: https://docs.docker.com/engine/network/drivers/bridge/
