"""
Comparison Module

This module provides comprehensive comparative analysis capabilities for the Dynamic Web Scraper,
including cross-site price comparison, product matching, and best deal recommendations.
"""

from .site_comparator import DealAnalysis, PriceComparison, ProductMatch, SiteComparator

__all__ = ["SiteComparator", "ProductMatch", "PriceComparison", "DealAnalysis"]
