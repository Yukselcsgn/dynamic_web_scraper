"""
Logging management for the dynamic e-commerce scraper project.

Modules:
- logging_manager: Configures and handles logging for scraper activities.
"""

# Import logging setup for centralized logging access
from .logging_manager import setup_logging

# Initialize logging configuration
logger = setup_logging()
