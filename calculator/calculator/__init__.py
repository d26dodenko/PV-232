"""Учебный проект: консольный калькулятор."""

from calculator.calculator import Calculator
from calculator.operations import (
    add,
    classify_number,
    divide,
    modulo,
    multiply,
    percent,
    power,
    sqrt,
    subtract,
)

__all__ = [
    "Calculator",
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "sqrt",
    "modulo",
    "percent",
    "classify_number",
]
