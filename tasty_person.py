def calculate_tastiness(
    height_cm: float,
    weight_kg: float,
    fat_percent: float,
    name: str,
    lifestyle: str,
) -> float:
    """
    Рассчитать условный индекс "вкусности" человека.

    Функция шуточная и отсылает к альбому четыре позиции Бруно,
    но оформлена по всем правилам тестирования.

    Бизнес-правила:
    1. height_cm должен быть в диапазоне 50..250, иначе ValueError.
    2. weight_kg должен быть в диапазоне 1..400, иначе ValueError.
    3. fat_percent должен быть в диапазоне 0..70, иначе ValueError.
    4. name должен быть непустой строкой, иначе ValueError.
    5. lifestyle должен быть "active" или "passive", иначе ValueError.
    6. Базовый индекс = weight_kg / (height_cm / 100) ** 2 (условный ИМТ).
    7. Нормированный ИМТ считается мягко, без резких порогов:
       norm_bmi = 100 / (1 + abs(bmi - 22) / 10).
    8. Жир влияет через множитель: fat_factor = 1 - fat_percent / 100.
    9. Образ жизни влияет через множитель:
       active -> 1.2, passive -> 0.8.
    10. Итог = norm_bmi * fat_factor * lifestyle_factor.
    11. Итог ограничивается диапазоном [0.0, 100.0].

    Аргументы:
        height_cm: рост в сантиметрах.
        weight_kg: вес в килограммах.
        fat_percent: процент жира в организме.
        name: имя человека.
        lifestyle: образ жизни ("active" или "passive").

    Возвращает:
        Итоговый индекс вкусности в диапазоне [0.0, 100.0].

    Исключения:
        ValueError: если хотя бы один параметр вне допустимого диапазона.
    """
    if not isinstance(height_cm, (int, float)) or height_cm < 50 or height_cm > 250:
        raise ValueError("height_cm must be in range 50..250")

    if not isinstance(weight_kg, (int, float)) or weight_kg < 1 or weight_kg > 400:
        raise ValueError("weight_kg must be in range 1..400")

    if not isinstance(fat_percent, (int, float)) or fat_percent < 0 or fat_percent > 70:
        raise ValueError("fat_percent must be in range 0..70")

    if not isinstance(name, str) or name == "":
        raise ValueError("name must be a non-empty string")

    if lifestyle not in ("active", "passive"):
        raise ValueError("lifestyle must be 'active' or 'passive'")

    bmi = weight_kg / (height_cm / 100) ** 2

    norm_bmi = 100 / (1 + abs(bmi - 22) / 10)

    # Множитель жира: 0% -> 1.0, 70% -> 0.3
    fat_factor = 1 - fat_percent / 100

    # Множитель образа жизни
    if lifestyle == "active":
        lifestyle_factor = 1.2
    else:
        lifestyle_factor = 0.8

    result = norm_bmi * fat_factor * lifestyle_factor

    result = max(0.0, result)
    result = min(100.0, result)

    return result