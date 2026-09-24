# Docker Volume

Образ: https://hub.docker.com/r/gilachone/simulative-practice-postgres

Dockerfile собирает PostgreSQL 16. seed.sql создает одну учебную строку, check.sql проверяет ее наличие. В evidence/verification.txt приведены команды и результаты четырех опытов.

| Опыт | Что происходит после пересоздания контейнера |
|---|---|
| Без явного монтирования | Новый контейнер получает новый анонимный том; таблицы в нем нет |
| Named volume | Подключаем тот же именованный том — строка остается |
| Anonymous volume | Сохраняем имя тома из inspect и явно подключаем его — строка остается |
| Bind mount | Подключаем ту же папку хоста — строка остается |

Важное уточнение: PostgreSQL 16 сам объявляет VOLUME. Поэтому «без монтирования» в данном образе не означает хранение БД в writable layer. Старый анонимный том после обычного docker rm остается, но новый контейнер сам его не находит. `docker rm -v` удаляет анонимный том. Именованный том обычным удалением контейнера не удаляется.

Воспроизводимые SQL-проверки в журнале выполнены через psql. Для выполнения тех же SQL через PgAdmin: опубликуйте порт контейнера только на localhost (`-p 127.0.0.1:15432:5432`), зарегистрируйте сервер с адресом 127.0.0.1, портом 15432, БД и пользователем practice и вашим локальным паролем, затем откройте seed.sql в Query Tool. После пересоздания выполните check.sql. При работе с VPS сначала используйте SSH-туннель, порт БД не требуется открывать в Интернет.

Пароль задается через POSTGRES_PASSWORD, а не в Dockerfile. Документация: https://docs.docker.com/engine/storage/volumes/

## Проверка через PgAdmin

Дополнительно таблица создана через Query Tool и проверена после пересоздания PostgreSQL с тем же именованным томом. Результат: `1 | saved data`, журнал `evidence/pgadmin.txt`.

Для запуска из этой папки:

```bash
python3 init_pgadmin.py
docker compose -f pgadmin-compose.yaml up -d
```

Откройте http://localhost:15080, сервер Docker Volume practice, БД practice → Query Tool. Выполните seed.sql и check.sql. Пароли генерируются локально в .env; повторный запуск init_pgadmin.py не нужен. Для пересоздания: `docker compose -f pgadmin-compose.yaml up -d --force-recreate postgres`. Повторите check.sql, при запросе PgAdmin нажмите Continue для переподключения. Остановка: `docker compose -f pgadmin-compose.yaml stop`.
