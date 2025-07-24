import unittest
from scraper.css_selectors.css_rules import CSSRuleManager

class TestCSSRuleManager(unittest.TestCase):
    def test_instantiation(self):
        manager = CSSRuleManager()
        self.assertIsInstance(manager, CSSRuleManager)

if __name__ == '__main__':
    unittest.main() 