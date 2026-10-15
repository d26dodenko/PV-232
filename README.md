# Лабораторная работа №1

Составление тест-кейсов для готового кода.

Выполнил студент группы ПВ-232 Письменный Антон.

Для работы взята функция `cost_bounds` из проекта GameForge. Она рассчитывает
стоимость использования модели с учётом кеша и длины запроса.

- [Отчёт](docs/report.md)
- [Исходный код](pricing.py)
- [Тесты](tests/test_pricing.py)
- [Результаты запуска](docs/results/pytest.txt)

## Запуск

Нужен Python 3.10 или новее.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -v
```

Для проверки покрытия:

```bash
coverage run -m pytest -v
coverage report -m
```

Все 50 тестов прошли. Покрытие модуля — 100% строк и ветвей, учитываемых coverage.
