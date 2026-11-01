import ast
import operator
from typing import Callable, Dict, List, Union

from calculator import operations

Number = Union[int, float]

_BINARY_OPS: Dict[type, Callable[[Number, Number], Number]] = {
    ast.Add: operations.add,
    ast.Sub: operations.subtract,
    ast.Mult: operations.multiply,
    ast.Div: operations.divide,
    ast.Mod: operations.modulo,
    ast.Pow: operations.power,
}

_UNARY_OPS: Dict[type, Callable[[Number], Number]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

class Calculator:
    def __init__(self) -> None:
        self._history: List[str] = []

    @property
    def history(self) -> List[str]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    def calculate(self, expression: str) -> Number:
        if not expression or not expression.strip():
            raise ValueError("Пустое выражение")
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Некорректное выражение: {expression}") from exc

        result = self._eval_node(tree.body)
        self._history.append(f"{expression.strip()} = {result}")

        return result

    def _eval_node(self, node: ast.AST) -> Number:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError("Допустимы только числа")
            return node.value

        if isinstance(node, ast.BinOp):
            op_func = _BINARY_OPS.get(type(node.op))
            if op_func is None:
                raise ValueError("Неподдерживаемая операция")
            return op_func(self._eval_node(node.left), self._eval_node(node.right))

        if isinstance(node, ast.UnaryOp):
            unary_func = _UNARY_OPS.get(type(node.op))
            if unary_func is None:
                raise ValueError("Неподдерживаемая операция")
            return unary_func(self._eval_node(node.operand))

        raise ValueError("Неподдерживаемая конструкция в выражении")