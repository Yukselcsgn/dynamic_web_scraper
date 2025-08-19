import unittest
from scraper.utils.html_utils import strip_tags


class TestHtmlUtils(unittest.TestCase):
    def test_strip_tags_basic(self):
        html = "<div>Hello <b>World</b>!</div>"
        self.assertEqual(strip_tags(html), "Hello World!")

    def test_strip_tags_empty(self):
        self.assertEqual(strip_tags(""), "")

    def test_strip_tags_no_tags(self):
        self.assertEqual(strip_tags("Just text"), "Just text")


if __name__ == "__main__":
    unittest.main()
