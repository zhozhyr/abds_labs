[![labs](https://github.com/zhozhyr/https://github.com/zhozhyr/abds_labs/actions/workflows/energosbyt.energosbyt.lab.yml/badge.svg)](https://github.com/zhozhyr/https://github.com/zhozhyr/abds_labs/actions/workflows/energosbyt.energosbyt.lab.yml)

## Лабораторная работа №1. SCD в ClickHouse

### Запуск

Команды:

- `make gen` - создать CSV в `data/`
- `make load` - загрузить CSV в ClickHouse
- `make run` - запустить сервис
- `make setup` - создать схему, сгенерировать и загрузить данные
- `make teardown` - удалить базу `energosbyt`
- `make check` - запустить Ruff, mypy и pytest

`make load` очищает таблицы перед загрузкой, поэтому повторный запуск не создаёт дубли

Swagger: `http://localhost:8080/docs`

Postman: [`api/energosbyt.postman_collection.json`](api/energosbyt.postman_collection.json)

## Ключи сортировки и партиционирование

| Таблица | `ORDER BY` | `PARTITION BY`           | причина                                                                  |
| --- | --- |--------------------------|--------------------------------------------------------------------------|
| `dim_realty` | `id` | -                        | поиск объекта по идентификатору                                          |
| `dim_gauges` | `id` | -                        | поиск счётчика по идентификатору                                         |
| `dim_tariffs` | `(id, valid_from)` | -                        | хранение версий тарифа по началу интервала                               |
| `dim_users` | `id` | -                        | замена версии пользователя по `updated_at`                               |
| `fact_gauge_bindings` | `(realty_id, gauge_id, created_at)` | -                        | установка и аннулирование имеют одинаковый ключ                          |
| `fact_meter_readings` | `(realty_id, reading_date)` | `toYYYYMM(reading_date)` | корректировка заменяет показание за тот же день; запросы идут по периоду |
| `fact_invoice` | `(realty_id, created_at)` | `toYYYYMM(created_at)`   | счета выбираются по объекту и сортируются по дате                        |