# Лабораторные работы — Прядко Богдан, ПВ-232

Все работы находятся в ветке `pryadko_bogdan`. В каждой папке сохранены задание преподавателя, отчёт и файлы решения.

## Тестирование ПО

| Работа | Задание | Решение |
|---|---|---|
| Laba-1. Тест-кейсы и модульное тестирование | [Laba-1.md](TestingPS/Laba-1/Laba-1.md) | [Отчёт и запуск](TestingPS/Laba-1/README.md) |
| Laba-2. Интеграционное и API-тестирование | [Laba-2.md](TestingPS/Laba-2/Laba-2.md) | [Отчёт и коллекция Postman](TestingPS/Laba-2/README.md) |
| Laba-3. UI-тесты и CI/CD | [Laba-3.md](TestingPS/Laba-3/Laba-3.md) | [Отчёт и интернет-магазин](TestingPS/Laba-3/README.md) |

## Спецификация

| Работа | Задание | Решение |
|---|---|---|
| Laba-1. Оценка качества ПО | [Laba-1.md](Specification/Laba-1/Laba-1.md) | [Отчёт и Snake](Specification/Laba-1/README.md) |
| Total. Проектирование EduTrack | [Total.md](Specification/Total/Total.md) | [Отчёт, диаграммы и план работ](Specification/Total/README.md) |

## Запуск и проверки

Каждая работа запускается из своей папки и использует собственные зависимости. Общего проекта и общего набора тестов для всех лабораторных нет.

**Тестирование, Laba-1** — Python 3.9+ и uv:

```bash
cd TestingPS/Laba-1
uv sync --locked --dev
uv run --locked pytest -v
```

**Тестирование, Laba-2** — импортировать коллекцию и окружение из `TestingPS/Laba-2/LabAPI_Pryadko` в Postman. Вариант запуска через Node.js:

```bash
cd TestingPS/Laba-2
npx --yes newman@6.2.3 run "LabAPI_Pryadko/LabAPI_Прядко.postman_collection.json" -e "LabAPI_Pryadko/LabAPI_Прядко.postman_environment.json"
```

Коллекция обращается к публичному Restful-Booker. В исходном отчёте зафиксированы 36 неуспешных проверок из-за расхождений API с ожиданиями. Эти проверки сохранены.

**Тестирование, Laba-3** — Node.js 24.x и Python 3.9+:

```bash
cd TestingPS/Laba-3
npm ci
npx playwright install --with-deps chromium
npm run check
```

Запуск магазина: `npm run dev`, адрес `http://127.0.0.1:5173`. Перед E2E приложение нужно остановить, поскольку тесты сами запускают серверы.

**Спецификация, Laba-1** — Python 3.9+, из корня репозитория:

```bash
cd Specification/Laba-1
python3 -m venv .venv
.venv/bin/python -m pip install -r snake/requirements-dev.txt
cd snake
../.venv/bin/python -m pytest --cov=snake_game --cov-branch
../.venv/bin/python -m snake_game
```

В Windows вместо `.venv/bin/python` используется `.venv/Scripts/python.exe`.

**Спецификация, Total** — проектная документация. Диаграммы находятся в `Specification/Total/edutrack_diagrams` в форматах PNG и draw.io, план задач — в CSV. Запуск приложения для этой работы не требуется.

## CI

В корневой `.github/workflows` находятся два независимых workflow:

- [tests.yml](.github/workflows/tests.yml) проверяет только `TestingPS/Laba-1`.
- [ci.yml](.github/workflows/ci.yml) проверяет только `TestingPS/Laba-3`, включая coverage, безопасность, сборку, integration и E2E.

Автоматические проверки запускаются при изменениях соответствующей лабораторной или её workflow. Изменения в спецификации или API-коллекции не запускают проверки магазина. Пути зависимостей, кешей и артефактов заданы отдельно для каждой работы.
