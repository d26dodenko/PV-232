# tf2_item.py

def calculate_item_cost(
    killstreak_tier: str,
    quality: str,
    has_spells: bool,
    strange_counter_count: int,
    strange_counter_value: float,
    base_cost: float,
    has_decorations: bool,
) -> float:
    """
    Рассчитать стоимость предмета из Team Fortress 2 в ключах.

    Бизнес-правила:
    1. killstreak_tier должен быть "serial", "specialized" или "professional", иначе ValueError.
    2. quality должен быть "unique" или "strange", иначе ValueError.
    3. strange_counter_count должен быть от 0 до 10 включительно, иначе ValueError.
    4. strange_counter_value должен быть от 0 до 1000 включительно, иначе ValueError.
    5. base_cost должен быть больше 0 и не больше 10000, иначе ValueError.
    6. Базовый множитель убийств:
       serial -> 1.0, specialized -> 1.5, professional -> 2.5.
    7. Множитель качества: unique -> 1.0, strange -> 1.8.
    8. Если есть спеллы, добавляется множитель 1.4.
    9. Если есть украшения, добавляется множитель 1.2.
    10. Стоимость странных счетчиков добавляется как:
        strange_counter_count * strange_counter_value * 0.01.
    11. Итог = (base_cost * killstreak_factor * quality_factor * spell_factor * decoration_factor)
        + counter_cost.
    12. Итог округляется до двух знаков после запятой.
    13. Итог не может быть отрицательным.

    Аргументы:
        killstreak_tier: набор убийц ("serial", "specialized", "professional").
        quality: качество предмета ("unique" или "strange").
        has_spells: наличие спеллов.
        strange_counter_count: количество странных счетчиков (0..10).
        strange_counter_value: стоимость одного странного счетчика (0..1000).
        base_cost: базовая стоимость предмета без всего (0..10000).
        has_decorations: наличие украшений.

    Возвращает:
        Итоговая стоимость предмета в ключах, округленная до двух знаков.

    Исключения:
        ValueError: если хотя бы один параметр вне допустимого диапазона.
    """
    if killstreak_tier not in ("serial", "specialized", "professional"):
        raise ValueError("killstreak_tier must be 'serial', 'specialized' or 'professional'")

    if quality not in ("unique", "strange"):
        raise ValueError("quality must be 'unique' or 'strange'")

    if not isinstance(strange_counter_count, int) or strange_counter_count < 0 or strange_counter_count > 10:
        raise ValueError("strange_counter_count must be in range 0..10")

    if not isinstance(strange_counter_value, (int, float)) or strange_counter_value < 0 or strange_counter_value > 1000:
        raise ValueError("strange_counter_value must be in range 0..1000")

    if not isinstance(base_cost, (int, float)) or base_cost <= 0 or base_cost > 10000:
        raise ValueError("base_cost must be in range 0..10000")

    if not isinstance(has_spells, bool) or not isinstance(has_decorations, bool):
        raise ValueError("has_spells and has_decorations must be bool")

    if killstreak_tier == "serial":
        killstreak_factor = 1.0
    elif killstreak_tier == "specialized":
        killstreak_factor = 1.5
    else:
        killstreak_factor = 2.5

    if quality == "unique":
        quality_factor = 1.0
    else:
        quality_factor = 1.8

    spell_factor = 1.4 if has_spells else 1.0
    decoration_factor = 1.2 if has_decorations else 1.0

    counter_cost = strange_counter_count * strange_counter_value * 0.01

    result = base_cost * killstreak_factor * quality_factor * spell_factor * decoration_factor
    result += counter_cost
    result = round(result, 2)
    result = max(0.0, result)

    return result