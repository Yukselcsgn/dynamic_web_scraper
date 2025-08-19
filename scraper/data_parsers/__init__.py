"""
Data parsers for the dynamic e-commerce scraper project.

Modules:
- data_parser: Base parser for data extraction.
- html_parser: HTML-specific data parsing functionality.
"""

# Import parsers for easier access
from .data_parser import save_data
from .html_parser import parse_html

__all__ = ["save_data", "parse_html"]
