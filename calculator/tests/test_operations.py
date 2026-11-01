import math
import unittest

from calculator import operations as op

class TestBasicOperations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(op.add(2, 3), 5)
        self.assertEqual(op.add(-2, 3), 1)
        self.assertAlmostEqual(op.add(0.1, 0.2), 0.3)

    def test_subtract(self):
        self.assertEqual(op.subtract(5, 3), 2)
        self.assertEqual(op.subtract(3, 5), -2)

    def test_multiply(self):
        self.assertEqual(op.multiply(4, 5), 20)
        self.assertEqual(op.multiply(-4, 5), -20)
        self.assertEqual(op.multiply(0, 100), 0)

class TestDivide(unittest.TestCase):
    def test_divide(self):
        self.assertEqual(op.divide(10, 2), 5)
        self.assertAlmostEqual(op.divide(1, 3), 0.3333333, places=6)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            op.divide(1, 0)

class TestModulo(unittest.TestCase):
    def test_modulo(self):
        self.assertEqual(op.modulo(10, 3), 1)
        self.assertEqual(op.modulo(9, 3), 0)

    def test_modulo_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            op.modulo(5, 0)

class TestPower(unittest.TestCase):
    def test_power(self):
        self.assertEqual(op.power(2, 10), 1024)
        self.assertEqual(op.power(5, 0), 1)
        self.assertAlmostEqual(op.power(2, -1), 0.5)
        self.assertEqual(op.power(-2, 3), -8)

    def test_zero_to_negative_power(self):
        with self.assertRaises(ZeroDivisionError):
            op.power(0, -1)

    def test_negative_base_fractional_exponent(self):
        with self.assertRaises(ValueError):
            op.power(-4, 0.5)

class TestSqrt(unittest.TestCase):
    def test_sqrt(self):
        self.assertEqual(op.sqrt(16), 4)
        self.assertEqual(op.sqrt(0), 0)
        self.assertTrue(math.isclose(op.sqrt(2), 1.41421356, rel_tol=1e-6))

    def test_sqrt_negative(self):
        with self.assertRaises(ValueError):
            op.sqrt(-1)

class TestPercent(unittest.TestCase):
    def test_percent(self):
        self.assertEqual(op.percent(200, 10), 20)
        self.assertEqual(op.percent(50, 0), 0)
        self.assertEqual(op.percent(80, 100), 80)

class TestClassifyNumber(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(op.classify_number(5), "Positive")

    def test_zero(self):
        self.assertEqual(op.classify_number(0), "Zero")

    def test_negative(self):
        self.assertEqual(op.classify_number(-5), "Negative")

if __name__ == "__main__":
    unittest.main()