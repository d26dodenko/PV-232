import math
from typing import Union

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    return a + b

def subtract(a: Number, b: Number) -> Number:
    return a - b

def multiply(a: Number, b: Number) -> Number:
    return a * b

def divide(a: Number, b: Number) -> float:
    if b == 0:
        raise ZeroDivisionError("Деление на ноль невозможно")
    return a / b

def modulo(a: Number, b: Number) -> Number:
    if b == 0:
        raise ZeroDivisionError("Остаток от деления на ноль невозможен")
    return a % b

def power(base: Number, exponent: Number) -> Number:
    if base == 0 and exponent < 0:
        raise ZeroDivisionError("0 нельзя возводить в отрицательную степень")
    if base < 0 and exponent != int(exponent):
        raise ValueError("Отрицательное число нельзя возводить в дробную степень")
    return base ** exponent

def sqrt(x: Number) -> float:
    if x < 0:
        raise ValueError("Корень из отрицательного числа не определён")
    return math.sqrt(x)

def percent(value: Number, pct: Number) -> float:
    return value * pct / 100

def classify_number(x: Number) -> str:
    if x > 0:
        return "Positive"
    elif x == 0:
        return "Zero"
    else:
        return "Negative"