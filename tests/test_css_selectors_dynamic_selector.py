import unittest
from scraper.css_selectors.dynamic_selector import DynamicSelector

class TestDynamicSelector(unittest.TestCase):
    def test_instantiation(self):
        selector = DynamicSelector()
        self.assertIsInstance(selector, DynamicSelector)

if __name__ == '__main__':
    unittest.main() 