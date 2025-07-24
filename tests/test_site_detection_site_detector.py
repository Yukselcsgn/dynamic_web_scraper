import unittest
from scraper.site_detection.site_detector import detect_site_structure

class TestSiteDetector(unittest.TestCase):
    def test_detect_site_structure_basic(self):
        html = '<html><head><title>Test</title></head><body><section id="main"></section></body></html>'
        result = detect_site_structure(html)
        self.assertIn('site_title', result)
        self.assertEqual(result['site_title'], 'Test')
        self.assertIn('main_sections', result)
        self.assertIn('main', result['main_sections'])

if __name__ == '__main__':
    unittest.main() 