def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def classify_number(x):
    if x > 0:
        return "Positive"
    elif x == 0:
        return "Zero"
    else:
        return "Negative"