# Docker Images

Два варианта файла message.txt → два образа с тегами 1.0 и 2.0.

```sh
docker build -t gilachone/simulative-practice-images:1.0 v1.0
docker build -t gilachone/simulative-practice-images:2.0 v2.0
docker run --rm gilachone/simulative-practice-images:1.0
docker run --rm gilachone/simulative-practice-images:2.0
docker image ls gilachone/simulative-practice-images
docker image inspect gilachone/simulative-practice-images:2.0
docker history gilachone/simulative-practice-images:2.0
```

Тег — имя ссылки на образ, а не неизменяемый идентификатор. Изменение файла создает новый слой и новый image ID; старый тег продолжает запускать старое содержимое. Проверены также tag, save/load и удаление временного тега (см. evidence/verification.txt).

Публичные образы: https://hub.docker.com/r/gilachone/simulative-practice-images/tags
