# DeliveryProject

DeliveryProject — HTTP API для регистрации посылок и расчёта стоимости их доставки. Регистрация выполняется асинхронно через Celery: сервис получает курс доллара к рублю, рассчитывает стоимость, сохраняет посылку в PostgreSQL и записывает данные расчёта в MongoDB.

## Возможности

- регистрация посылки с привязкой к сессии пользователя через cookie `session_id`;
- асинхронный расчёт стоимости доставки по формуле
  `(вес × 0,5 + стоимость содержимого в USD × 0,01) × курс USD/RUB`;
- получение списка посылок текущей сессии с пагинацией и фильтром по типу;
- получение посылки по UUID;
- однократное назначение транспортной компании посылке;
- получение справочника типов посылок;
- получение суммы рассчитанной стоимости доставок выбранного типа за последние три дня;
- почасовое обновление курса USD/RUB и кеширование курса в Redis на 3900 секунд;
- журналирование HTTP-запросов с заголовком `X-Request-ID`.

## Технологии

- Python `>=3.13,<3.14`, FastAPI, Uvicorn и Pydantic Settings;
- PostgreSQL 17, SQLAlchemy 2 и Alembic;
- MongoDB 8.3.8, PyMongo и Beanie;
- Redis 8.8.1;
- RabbitMQ 4.3.4 и Celery 5.6;
- aiohttp для получения курса валют;
- Poetry 2.4.1 в Docker-сборке;
- pytest, pytest-asyncio и pytest-cov;
- Ruff, Mypy, Bandit и Radon.

Приложение разделено на доменный, прикладной, инфраструктурный и HTTP-слои.

## Требования

### Запуск через Docker

- Docker Engine;
- Docker Compose v2.

Минимальные поддерживаемые версии Docker и Compose в репозитории не указаны.

### Локальный запуск

- Python 3.13;
- Poetry;
- доступные экземпляры PostgreSQL, MongoDB, Redis и RabbitMQ;
- POSIX-совместимое окружение. Цели `Makefile` используют `make`, `grep` и `awk`.

## Переменные окружения

Приложение читает локальные настройки из `.env`. Docker Compose читает `.env.docker`. Оба файла исключены из Git. В репозитории находятся шаблоны `.env_example` и `.env.docker_example`.

| Переменная | Обязательна | Назначение |
| --- | --- | --- |
| `POSTGRES_HOST` | да | Хост PostgreSQL |
| `POSTGRES_PORT` | да | Порт PostgreSQL |
| `POSTGRES_USER` | да | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | да | Пароль PostgreSQL |
| `POSTGRES_DB` | да | Имя базы PostgreSQL |
| `REDIS_URL` | да | DSN Redis; используется как кеш и Celery backend |
| `MONGO_URL` | да | DSN MongoDB |
| `MONGO_DB_NAME` | да | Имя базы MongoDB |
| `RABBIT_URL` | да | AMQP DSN брокера Celery |
| `CURRENCY_URL` | да | URL JSON-источника курса USD/RUB |
| `RABBITMQ_DEFAULT_USER` | только Docker | Пользователь создаваемого контейнера RabbitMQ |
| `RABBITMQ_DEFAULT_PASS` | только Docker | Пароль создаваемого контейнера RabbitMQ |
| `DB_POOL_SIZE` | нет | Размер пула PostgreSQL, допустимо от 1 до 50; по умолчанию в коде `10`, в шаблонах `20` |
| `CORS_ORIGINS` | нет | JSON-массив разрешённых CORS origin; по умолчанию в коде `["*"]` |
| `MAX_RETRIES` | нет | Числовая настройка, по умолчанию `5`; в текущем коде не используется |
| `APP_ENV` | нет | При значении `prod` включает JSON-формат логов; по умолчанию `dev` |
| `DEBUG` | да | Булево значение `true` или `false` |
| `LOG_LEVEL` | нет | Уровень Loguru, по умолчанию `INFO` |

Безопасный пример `.env.docker`:

```dotenv
POSTGRES_HOST=postgresql
POSTGRES_PORT=5432
POSTGRES_USER=delivery
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_DB=delivery

REDIS_URL=redis://redis:6379/0

MONGO_URL=mongodb://mongodb:27017
MONGO_DB_NAME=delivery

RABBITMQ_DEFAULT_USER=delivery
RABBITMQ_DEFAULT_PASS=CHANGE_ME
RABBIT_URL=amqp://delivery:CHANGE_ME@rabbitmq:5672//

DB_POOL_SIZE=20
CORS_ORIGINS=["http://localhost:8000"]
MAX_RETRIES=5
CURRENCY_URL=https://www.cbr-xml-daily.ru/daily_json.js

APP_ENV=prod
DEBUG=false
LOG_LEVEL=INFO
```

`CHANGE_ME` — только плейсхолдер. Перед запуском задайте собственные значения и не добавляйте `.env` или `.env.docker` в Git. Для локального запуска замените имена Docker-сервисов (`postgresql`, `mongodb`, `redis`, `rabbitmq`) адресами реально запущенных сервисов, например `127.0.0.1`.

## Установка и запуск через Docker

Это наиболее полный способ запуска, зафиксированный в репозитории. Compose запускает миграции, API, Celery worker, Celery beat и все хранилища.

1. Создайте конфигурацию:

```bash
cp .env.docker_example .env.docker
```

2. Заполните `.env.docker`, используя безопасный пример выше.

3. Соберите и запустите сервисы:

```bash
docker compose up --build -d
```

4. Проверьте состояние и логи:

```bash
docker compose ps
docker compose logs -f app worker beat migration
```

Миграции Alembic применяются сервисом `migration` до запуска API и worker. API публикуется на `http://localhost:8000`; порты PostgreSQL, MongoDB, RabbitMQ и Redis наружу не публикуются.

Остановить контейнеры без удаления именованных томов:

```bash
docker compose down
```

## Локальная установка

1. Установите зависимости из `pyproject.toml` и `poetry.lock`:

```bash
poetry install
```

2. Создайте локальную конфигурацию:

```bash
cp .env_example .env
```

3. Заполните `.env` адресами доступных PostgreSQL, MongoDB, Redis и RabbitMQ. Docker Compose из этого репозитория не публикует их порты на хост, поэтому для полностью локального запуска инфраструктуру необходимо предоставить отдельно.

4. Примените миграции:

```bash
poetry run alembic -c alembic.ini upgrade head
```

Миграции создают таблицы и добавляют три типа посылок: `Одежда`, `Электроника` и `Разное`.

## Запуск в режиме разработки

Запустите API с автоматической перезагрузкой:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

В отдельных терминалах запустите обработчик задач и планировщик:

```bash
poetry run celery -A app.infrastructure.celery_app:celery_app worker --loglevel=INFO
```

```bash
poetry run celery -A app.infrastructure.celery_app:celery_app beat --loglevel=INFO
```

Интерактивная документация FastAPI доступна по адресу `http://localhost:8000/docs`.

## Запуск без режима разработки

Команда API, зафиксированная в `Dockerfile`, не включает hot reload:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Для регистрации посылок нужен Celery worker. Celery beat нужен для почасовой постановки задачи обновления курса.

> **TODO:** в репозитории нет отдельной production-конфигурации с TLS, reverse proxy, несколькими процессами API и описанной политикой развёртывания. Текущий `docker-compose.yml` использует образ с тегом `delivery-app:dev` и не подтверждает готовность конфигурации к публичной эксплуатации.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `POST` | `/parcels` | Поставить регистрацию посылки в очередь; возвращает UUID и устанавливает `session_id` |
| `GET` | `/parcels` | Получить посылки текущей сессии |
| `GET` | `/parcels/{parcel_id}` | Получить посылку по UUID |
| `PATCH` | `/parcels/{parcel_id}/company` | Назначить транспортную компанию |
| `GET` | `/delivery_prices` | Получить сумму стоимости доставок типа за последние три дня |
| `GET` | `/parcels_types` | Получить справочник типов посылок |

Параметры `GET /parcels`:

- `limit` — от 1 до 100, по умолчанию 5;
- `offset` — неотрицательное число, по умолчанию 0;
- `parcel_type` — повторяемый фильтр со значениями `Одежда`, `Электроника` или `Разное`.

### Примеры запросов

Зарегистрировать посылку:

```bash
curl -i -X POST 'http://localhost:8000/parcels' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Холодильник Haier",
    "weight": "50.00",
    "content_price_usd": "1000.00",
    "parcel_type_id": 2
  }'
```

Ответ имеет статус `201` и содержит UUID строкой:

```json
"11111111-1111-1111-1111-111111111111"
```

Задача выполняется асинхронно, поэтому данные могут появиться в `GET /parcels/{parcel_id}` не сразу. Скопируйте значение `session_id` из заголовка `Set-Cookie` первого ответа для запросов списка:

```bash
curl --get 'http://localhost:8000/parcels' \
  -H 'Cookie: session_id=536fb57b-2711-4237-ae38-2e710e68fb03' \
  --data-urlencode 'limit=5' \
  --data-urlencode 'offset=0' \
  --data-urlencode 'parcel_type=Электроника'
```

Получить одну посылку:

```bash
curl 'http://localhost:8000/parcels/11111111-1111-1111-1111-111111111111'
```

Назначить компанию:

```bash
curl -X PATCH 'http://localhost:8000/parcels/11111111-1111-1111-1111-111111111111/company' \
  -H 'Content-Type: application/json' \
  -d '{"company_id": 3}'
```

Получить сумму по типу посылки:

```bash
curl --get 'http://localhost:8000/delivery_prices' \
  --data-urlencode 'parcel_type_id=1'
```

## Тесты и проверки качества

Запустить тесты:

```bash
poetry run pytest
```

Запустить тесты с отчётом о покрытии:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Тесты находятся в `src/tests` и проверяют HTTP API. Перед импортом приложения настройки валидируются, а при запуске lifespan приложение выполняет `ping` MongoDB, поэтому требуется корректный `.env` и доступная MongoDB.

Проверить код без автоматических исправлений:

```bash
poetry run ruff check src/app
poetry run ruff format --check src/app
poetry run mypy src/app
```

Применить линт-исправления и форматирование:

```bash
make lint
make fmt
```

Остальные цели качества:

```bash
make type
make security
make cc
make mi
make hal
make raw
```

Полная локальная проверка:

```bash
make check
```

`make check` запускает Ruff с автоисправлением и форматированием, затем Mypy, Bandit и метрики Radon, поэтому команда может изменить файлы в `src/app`.

Настроить и вручную запустить pre-commit hook, который вызывает `make check`:

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Структура проекта

```text
.
├── src/
│   ├── app/
│   │   ├── application/        # прикладные сервисы и интерфейсы репозиториев
│   │   ├── domain/             # сущности и формула расчёта стоимости
│   │   ├── infrastructure/     # PostgreSQL, MongoDB, Redis, Celery и валютный клиент
│   │   ├── presentation/       # FastAPI-роуты, зависимости и Pydantic-схемы
│   │   ├── tasks/              # Celery-задачи и их зависимости
│   │   ├── utils/              # логирование, middleware и обработчики ошибок
│   │   ├── config.py           # загрузка и валидация настроек
│   │   └── main.py             # создание FastAPI-приложения
│   ├── alembic/                # окружение и версии миграций
│   └── tests/                  # асинхронные API-тесты
├── alembic.ini                 # конфигурация Alembic
├── docker-compose.yml          # API, worker, beat и инфраструктурные сервисы
├── Dockerfile                  # multi-stage образ Python 3.13
├── Makefile                    # линтинг, форматирование и quality gates
├── pyproject.toml              # метаданные, зависимости и настройки инструментов
├── poetry.lock                 # зафиксированные Poetry-зависимости
├── requirements.txt            # зафиксированный список pip-зависимостей
└── rabbitmq.conf               # совместимость Celery 5.6 с RabbitMQ 4.3
```

## Типичные проблемы

### Ошибка валидации настроек при импорте приложения

Все обязательные переменные должны быть заполнены до запуска. В частности, `DEBUG` принимает булево значение, а не произвольную строку:

```dotenv
DEBUG=false
```

### API не запускается без MongoDB

При старте приложение выполняет `ping` MongoDB и инициализирует Beanie. Проверьте `MONGO_URL`, `MONGO_DB_NAME` и состояние контейнера:

```bash
docker compose ps mongodb
docker compose logs mongodb
```

### `POST /parcels` вернул UUID, но посылка ещё не читается

Регистрация выполняется в Celery worker. Проверьте worker, RabbitMQ, Redis, PostgreSQL, MongoDB и доступность `CURRENCY_URL`:

```bash
docker compose ps worker rabbitmq redis postgresql mongodb
docker compose logs worker rabbitmq
```

### Список посылок пуст при запросе из браузера по HTTP

Cookie `session_id` создаётся с флагами `HttpOnly` и `Secure`. Браузер не отправляет Secure-cookie по обычному HTTP. Для браузерного клиента используйте HTTPS; при ручной локальной проверке можно передать заголовок `Cookie`, как в примере API выше.

### Ошибка миграции PostgreSQL

Проверьте параметры `POSTGRES_*`, доступность базы и журнал сервиса миграций:

```bash
docker compose logs migration postgresql
```

### Celery не работает с RabbitMQ 4.3

В репозитории есть `rabbitmq.conf`, разрешающий устаревшие типы очередей, которые использует Celery 5.6. Docker Compose уже монтирует этот файл. При внешнем RabbitMQ эквивалентную настройку необходимо выполнить отдельно.

## TODO

- Добавить подтверждённую production-схему развёртывания.
- Добавить файл лицензии и правила участия в разработке: сейчас такие файлы в репозитории отсутствуют, поэтому условия распространения и приёма изменений не определены.
