# Кабачок

## Запуск

1. Создать `.env` файл с переменными `POSTGRES_PASSWORD` и `BOT_TOKEN`.
1. Установить зависимости: `rye sync`.
1. Собрать контейнеры: `./buils.sh`.
1. Запустить контейнеры: `docker-compose docker-compose.yaml up`.

Для тестов можно использовать _playground_: `docker-compose -f docker-compose.yaml -f playground-compose.yaml up`.

Для получения более полной информации о системе с базой данный, необходимо установить на неё пакет `postgresql-plpython3-16`.


## Текущие задачи

1. Довести все существующие alert-ы до рабочего состояния
    - [ ] CPU Usage
    - [ ] Disk space
    - [x] Active peers
    - [ ] LWLOCK transactions
    - [ ] Long transactions
    - [x] DB is unavailable

2. ~Рефакторинг бэкэнда (улучшение логики healthcheck)~
3. Redis (цель: динамика использования + графики)
4. Генерация изображений на фронтэнде (Seaborn)
5. ~Сделать рабочий конфиг в виде файла для быстрой загрузки и теста БД~
6. Возвращение uuid-а ошибки на фронт в случае неудачной работы сервиса
7. Причесать сообщения на фронтэнде (Emoji)
8. Выводить AlertType с эмодзи

### Disk usage alert
- [x] INSERTS
- [ ] Playground (забитый диск + низкий кэп)

### Long transactions

- [x] PG pause
- [x] Playground
- [ ] Завершение долгих транзакций с бэкэнда (+ ручки)
- [ ] Отображение долгих транзакций + взаимодействие с ручками (завершить все долгие + завершение каждой по отдельности)

### CPU Usage

- [ ] Нужны ресурсоемкие операции
- [ ] Playground (low CPU)
