import math

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Деление на ноль невозможно")
    return a / b

def power(base, exponent):
    if exponent < 0 and base == 0:
        raise ValueError("Ноль нельзя возводить в отрицательную степень")
    return base ** exponent

def square_root(a):
    if a < 0:
        raise ValueError("Корень из отрицательного числа не определен")
    return math.sqrt(a)

def main():
    operations = {
        "1": ("Сложение", add),
        "2": ("Вычитание", subtract),
        "3": ("Умножение", multiply),
        "4": ("Деление", divide),
        "5": ("Возведение в степень", power),
        "6": ("Квадратный корень (введите 0 вторым числом)", lambda x, y: square_root(x))
    }

    print("Доступные операции:")
    for key, (name, _) in operations.items():
        print(f"  {key}. {name}")

    choice = input("Выберите операцию (1-6): ").strip()
    if choice not in operations:
        print("Неверный выбор")
        return

    try:
        a = float(input("Введите первое число: "))
        b = float(input("Введите второе число (для корня введите 0): "))
        name, func = operations[choice]
        print(f"Результат ({name}): {func(a, b)}")
    except ValueError as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()