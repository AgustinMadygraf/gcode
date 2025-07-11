"""
Tests for PathTransformStrategyPort and a concrete implementation.
"""
import unittest
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort

class IdentityTransformStrategy(PathTransformStrategyPort):
    def transform(self, x: float, y: float) -> tuple[float, float]:
        return x, y

class NoTransformStrategy(PathTransformStrategyPort):
    pass  # Does not implement transform

class TestPathTransformStrategyPort(unittest.TestCase):
    def test_identity_transform(self):
        strategy = IdentityTransformStrategy()
        x, y = 5.0, -3.2
        result = strategy.transform(x, y)
        self.assertEqual(result, (x, y))
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(v, float) for v in result))

    def test_cannot_instantiate_abstract(self):
        with self.assertRaises(TypeError):
            PathTransformStrategyPort()

    def test_missing_transform_raises(self):
        with self.assertRaises(TypeError):
            NoTransformStrategy()

    def test_transform_returns_tuple_of_floats(self):
        strategy = IdentityTransformStrategy()
        result = strategy.transform(1.1, 2.2)
        self.assertIsInstance(result, tuple)
        self.assertTrue(all(isinstance(v, float) for v in result))

if __name__ == "__main__":
    unittest.main()
