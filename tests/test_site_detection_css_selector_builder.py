import unittest
from scraper.site_detection.css_selector_builder import build_selector


class TestCSSSelectorBuilder(unittest.TestCase):
    def test_build_selector_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            build_selector(None)


if __name__ == "__main__":
    unittest.main()
