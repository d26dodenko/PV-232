# Snake

Python 3.9+, Pygame. Из корня репозитория:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r snake/requirements-dev.txt
cd snake
../.venv/bin/python -m snake_game
```

Стрелки/WASD — движение, Enter — старт, Space/P — пауза, R — перезапуск,
Esc — меню/выход. Скорость: 1/2/3 в меню или на паузе. Рекорд: `~/.mint_snake/best.json`.

Проверка из папки `snake/`:

```sh
../.venv/bin/python -m pytest --cov=snake_game --cov-branch
```

[Отчёт по лабораторной](../README.md).
