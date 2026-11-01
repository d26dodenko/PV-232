import unittest

from calculator import Calculator
from calculator import cli

class TestProcessCommand(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_expression(self):
        self.assertEqual(cli.process_command(self.calc, "2 + 2"), "4")

    def test_exit_commands(self):
        self.assertIsNone(cli.process_command(self.calc, "exit"))
        self.assertIsNone(cli.process_command(self.calc, "QUIT"))

    def test_help(self):
        self.assertEqual(cli.process_command(self.calc, "help"), cli.HELP_TEXT)

    def test_history_empty_and_filled(self):
        self.assertEqual(cli.process_command(self.calc, "history"), "История пуста")
        cli.process_command(self.calc, "1 + 2")
        self.assertEqual(cli.process_command(self.calc, "history"), "1 + 2 = 3")

    def test_clear(self):
        cli.process_command(self.calc, "1 + 2")
        self.assertEqual(cli.process_command(self.calc, "clear"), "История очищена")
        self.assertEqual(self.calc.history, [])

    def test_errors_are_reported(self):
        self.assertIn("Ошибка", cli.process_command(self.calc, "1 / 0"))
        self.assertIn("Ошибка", cli.process_command(self.calc, "2 +"))
        self.assertIn("Ошибка", cli.process_command(self.calc, "abc"))

class TestRun(unittest.TestCase):
    @staticmethod
    def _run(lines):
        inputs = iter(lines)
        outputs = []

        def fake_input(_prompt):
            try:
                return next(inputs)
            except StopIteration:
                raise EOFError

        cli.run(input_func=fake_input, output_func=outputs.append)
        return outputs

    def test_session(self):
        out = self._run(["2 + 3", "history", "exit", "999"])
        self.assertEqual(out[1], "5")
        self.assertEqual(out[2], "2 + 3 = 5")
        self.assertEqual(len(out), 3)

    def test_eof_ends_session(self):
        out = self._run([])
        self.assertEqual(len(out), 1)

if __name__ == "__main__":
    unittest.main()