import unittest

from calculator import Calculator

class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_simple_expressions(self):
        self.assertEqual(self.calc.calculate("2 + 3"), 5)
        self.assertEqual(self.calc.calculate("10 - 4"), 6)
        self.assertEqual(self.calc.calculate("6 * 7"), 42)
        self.assertEqual(self.calc.calculate("9 / 3"), 3)
        self.assertEqual(self.calc.calculate("10 % 4"), 2)
        self.assertEqual(self.calc.calculate("2 ** 5"), 32)

    def test_operator_precedence(self):
        self.assertEqual(self.calc.calculate("2 + 3 * 4"), 14)
        self.assertEqual(self.calc.calculate("(2 + 3) * 4"), 20)

    def test_unary_operators(self):
        self.assertEqual(self.calc.calculate("-5 + 2"), -3)
        self.assertEqual(self.calc.calculate("+5"), 5)
        self.assertEqual(self.calc.calculate("--5"), 5)

    def test_float_numbers(self):
        self.assertAlmostEqual(self.calc.calculate("0.1 + 0.2"), 0.3)

    def test_whitespace_is_ignored(self):
        self.assertEqual(self.calc.calculate("  1+1  "), 2)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.calculate("1 / 0")

    def test_empty_expression(self):
        with self.assertRaises(ValueError):
            self.calc.calculate("")
        with self.assertRaises(ValueError):
            self.calc.calculate("   ")

    def test_syntax_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate("2 +")

    def test_unsupported_constructs(self):
        for expr in ("abs(-1)", "x + 1", "'a' + 'b'", "True + 1", "1 // 2", "~1"):
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError):
                    self.calc.calculate(expr)

    def test_code_injection_is_blocked(self):
        with self.assertRaises(ValueError):
            self.calc.calculate("__import__('os').system('echo hacked')")

class TestHistory(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_history_records_results(self):
        self.calc.calculate("1 + 1")
        self.calc.calculate("2 * 3")
        self.assertEqual(self.calc.history, ["1 + 1 = 2", "2 * 3 = 6"])

    def test_failed_calculation_not_in_history(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.calculate("1 / 0")
        self.assertEqual(self.calc.history, [])

    def test_history_is_a_copy(self):
        self.calc.calculate("1 + 1")
        self.calc.history.append("hack")
        self.assertEqual(len(self.calc.history), 1)

    def test_clear_history(self):
        self.calc.calculate("1 + 1")
        self.calc.clear_history()
        self.assertEqual(self.calc.history, [])


if __name__ == "__main__":
    unittest.main()