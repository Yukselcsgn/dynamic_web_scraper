"""
Site detection utilities for identifying e-commerce site structures.

Modules:
- site_detector: Detects specific e-commerce site configurations.
- site_config: Stores site-specific configurations.
"""

# Automatically import core detector functionality
from .site_detector import detect_site_structure

__all__ = ["detect_site_structure"]
