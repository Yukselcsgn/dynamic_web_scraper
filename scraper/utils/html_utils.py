"""
HTML utility functions for the dynamic web scraper project.
"""

from bs4 import BeautifulSoup


def strip_tags(html):
    """Remove all HTML tags from a string and return plain text."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()
