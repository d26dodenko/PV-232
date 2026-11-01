from typing import Callable, Optional
from calculator import Calculator

HELP_TEXT = (
    "Введите выражение, например: 2 + 3 * (4 - 1)\n"
    "Операции: + - * / % **\n"
    "Команды: history - показать историю, clear - очистить историю, "
    "help - справка, exit - выход"
)

def process_command(calc: Calculator, line: str) -> Optional[str]:
    command = line.strip()
    lowered = command.lower()

    if lowered in ("exit", "quit"):
        return None
    if lowered == "help":
        return HELP_TEXT
    if lowered == "history":
        history = calc.history
        return "\n".join(history) if history else "История пуста"
    if lowered == "clear":
        calc.clear_history()
        return "История очищена"

    try:
        return str(calc.calculate(command))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        return f"Ошибка: {exc}"

def run(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    calc = Calculator()
    output_func("Калькулятор. Введите help для справки.")
    while True:
        try:
            line = input_func("> ")
        except EOFError:
            break
        result = process_command(calc, line)
        if result is None:
            break
        output_func(result)

if __name__ == "__main__":
    run()