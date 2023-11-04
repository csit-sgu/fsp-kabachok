# Кабачок

## Запуск

1. Создать `.env` файл с переменными `POSTGRES_PASSWORD` и `BOT_TOKEN`.
1. Установить зависимости: `rye sync`.
1. Собрать контейнеры: `./buils.sh`.
1. Запустить контейнеры: `docker-compose docker-compose.yaml up`.

Для тестов можно использовать _playground_: `docker-compose -f docker-compose.yaml -f playground-compose.yaml up`.

Для получения более полной информации о системе с базой данный, необходимо установить на неё пакет `postgresql-plpython3-16`.
