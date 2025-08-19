import unittest
from scraper.css_selectors.css_selector_generator import generate_selector


class TestCSSSelectorGenerator(unittest.TestCase):
    def test_generate_selector_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            generate_selector(None)


if __name__ == "__main__":
    unittest.main()
