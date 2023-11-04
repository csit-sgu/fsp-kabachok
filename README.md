# Кабачок

## Запуск

1. Создать `.env` файл с одной переменной `POSTGRES_PASSWORD`.
2. Создать `tgbot/.env` файл с переменными `BOT_TOKEN` и `BACKEND_URL_PREFIX=http://alarmist:8000/api`.
3. Установить зависимости: `rye sync`.
4. Собрать контейнеры: `./buils.sh`.
5. Запустить контейнеры: `docker-compose up`.
