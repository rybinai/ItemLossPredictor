# Item Loss Predictor

Предсказывает расходы за отказ от покупки товара. На вход часть признаков из HTTP-запроса,
остальное (историческая доля возвратов, средние расходы за 30 дней) сервис сам достаёт из БД по
`item_id`, дальше всё это идёт в готовую ML-модель.

## Переменные окружения

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - учётные данные Postgres, использует `compose.yaml`
- `DATABASE_URL` - строка подключения к БД, например `postgresql+psycopg://user:pass@host:5432/db`
- `MODEL_PATH` - путь к `model.joblib`
- `MODEL_METADATA_PATH` - путь к `model_metadata.json`, необязательна, по умолчанию
  `artifacts/model_metadata.json`

Скопировать `.env.example` в `.env` перед первым запуском.

## Запуск

```
docker compose up -d --build
```

Сервис на `http://localhost:8000`, документация API - `http://localhost:8000/docs`.

## Загрузка признаков

```
docker compose exec app python -m app.features_loader artifacts/item_features.csv
```

Не запускается автоматически - команда для первичной загрузки и для обновления признаков при
изменении CSV. Обновляет записи по `item_id`. Строки с пустыми обязательными полями, неверным
типом, `historical_return_rate` вне `[0, 1]` или отрицательным `avg_item_losses_30d` пропускаются.

## Тесты

```
docker compose up -d db
pytest -v
```

Каждый тест пересоздаёт схему БД.


## Линтер

```
ruff check .
```