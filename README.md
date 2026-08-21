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
- pytest, pytest-asyncio, pytest-cov и `httpx2`;
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

## Установка и запуск через Docker

Это наиболее полный способ запуска, зафиксированный в репозитории. Compose запускает миграции, API, Celery worker, Celery beat и все хранилища.

1. Создайте конфигурацию:

```bash
cp .env.docker_example .env.docker
```

2. Заполните обязательные пустые значения в `.env.docker`, используя отдельные
   учётные данные для этого окружения, и не добавляйте файл в Git.

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

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `POST` | `/parcels` | Поставить регистрацию посылки в очередь; возвращает UUID и создаёт `session_id`, если cookie отсутствует |
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

Тесты находятся в `src/tests` и отправляют запросы непосредственно в ASGI-приложение через `httpx2.ASGITransport`. При импорте приложения настройки валидируются, поэтому обязательные переменные должны быть заданы через `.env` или окружение. Текущий транспорт не запускает FastAPI lifespan, а зависимости PostgreSQL и MongoDB и отправка Celery-задачи подменяются моками. Поэтому для существующих тестов доступные PostgreSQL, MongoDB, Redis и RabbitMQ не требуются.

Текущий набор тестов не проверяет реальную цепочку `Celery → PostgreSQL → MongoDB`, а также не содержит позитивного сценария `GET /parcels/{parcel_id}`.

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

Комплексная проверка качества без запуска pytest:

```bash
make check
```

`make check` запускает Ruff с автоисправлением и форматированием, затем Mypy, Bandit и метрики Radon, поэтому команда может изменить файлы в `src/app`. Тесты в эту цель не входят.

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

При реальном старте через Uvicorn FastAPI lifespan выполняет `ping` MongoDB и инициализирует Beanie. Текущие тесты lifespan не запускают. Если сервер не стартует, проверьте `MONGO_URL`, `MONGO_DB_NAME` и состояние контейнера:

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
