import unittest
from scraper.site_detection.html_analyzer import analyze_html

class TestHTMLAnalyzer(unittest.TestCase):
    def test_analyze_html_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            analyze_html(None)

if __name__ == '__main__':
    unittest.main() 