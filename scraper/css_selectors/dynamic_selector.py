"""
Dynamic selector logic for the dynamic web scraper project.
"""

from bs4 import BeautifulSoup, Tag
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse


class DynamicSelector:
    """Dynamic selector system that adapts to different website structures."""

    def __init__(self):
        """Initialize the dynamic selector system."""
        self.known_patterns = {
            "ecommerce": {
                "product_containers": [
                    r"product",
                    r"item",
                    r"card",
                    r"listing",
                    r"goods",
                    r"merchandise",
                    r"product-item",
                    r"product-card",
                    r"item-card",
                    r"listing-item",
                ],
                "product_titles": [
                    r"title",
                    r"name",
                    r"product-name",
                    r"item-title",
                    r"card-title",
                    r"product-title",
                    r"heading",
                    r"product-heading",
                ],
                "product_prices": [
                    r"price",
                    r"cost",
                    r"amount",
                    r"value",
                    r"product-price",
                    r"item-price",
                    r"card-price",
                    r"listing-price",
                ],
                "product_images": [
                    r"image",
                    r"img",
                    r"photo",
                    r"picture",
                    r"product-image",
                    r"item-image",
                    r"card-image",
                    r"listing-image",
                ],
                "product_links": [
                    r"link",
                    r"url",
                    r"href",
                    r"product-link",
                    r"item-link",
                    r"card-link",
                    r"listing-link",
                ],
            }
        }

        self.site_cache = {}

    def detect_site_type(self, url: str, html_content: str) -> str:
        """
        Detect the type of website based on URL and content.

        Args:
            url: Website URL
            html_content: HTML content of the page

        Returns:
            String indicating site type (e.g., 'ecommerce', 'blog', 'news')
        """
        domain = urlparse(url).netloc.lower()

        # Check for known e-commerce domains
        ecommerce_domains = [
            "amazon",
            "ebay",
            "walmart",
            "target",
            "bestbuy",
            "newegg",
            "etsy",
            "shopify",
            "magento",
            "woocommerce",
            "prestashop",
            "teknosa",
            "vatanbilgisayar",
            "hepsiburada",
            "trendyol",
        ]

        for domain_keyword in ecommerce_domains:
            if domain_keyword in domain:
                return "ecommerce"

        # Check HTML content for e-commerce indicators
        soup = BeautifulSoup(html_content, "html.parser")

        # Look for shopping cart, product, price indicators
        ecommerce_indicators = [
            "add to cart",
            "buy now",
            "shopping cart",
            "checkout",
            "product",
            "price",
            "sale",
            "discount",
            "shipping",
        ]

        text_content = soup.get_text().lower()
        indicator_count = sum(
            1 for indicator in ecommerce_indicators if indicator in text_content
        )

        if indicator_count >= 3:
            return "ecommerce"

        return "unknown"

    def generate_selectors(
        self, html_content: str, site_type: str = "ecommerce"
    ) -> Dict[str, List[str]]:
        """
        Generate CSS selectors for different elements based on site type.

        Args:
            html_content: HTML content to analyze
            site_type: Type of website

        Returns:
            Dictionary with element types as keys and lists of selectors as values
        """
        soup = BeautifulSoup(html_content, "html.parser")
        selectors = {
            "product_containers": [],
            "product_titles": [],
            "product_prices": [],
            "product_images": [],
            "product_links": [],
        }

        if site_type not in self.known_patterns:
            return selectors

        patterns = self.known_patterns[site_type]

        # Generate selectors for each element type
        for element_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                # Find elements by class name pattern
                elements = soup.find_all(class_=re.compile(pattern, re.I))

                for element in elements:
                    selector = self._generate_element_selector(element)
                    if selector and selector not in selectors[element_type]:
                        selectors[element_type].append(selector)

                # Also check for elements with pattern in their ID
                elements_by_id = soup.find_all(id=re.compile(pattern, re.I))
                for element in elements_by_id:
                    selector = self._generate_element_selector(element)
                    if selector and selector not in selectors[element_type]:
                        selectors[element_type].append(selector)

        return selectors

    def _generate_element_selector(self, element: Tag) -> str:
        """
        Generate a CSS selector for a specific element.

        Args:
            element: BeautifulSoup Tag element

        Returns:
            CSS selector string
        """
        if not element or not element.name:
            return ""

        # Start with tag name
        selector = element.name

        # Add ID if present (highest specificity)
        if element.get("id"):
            return f"#{element['id']}"

        # Add classes if present
        classes = element.get("class", [])
        if classes:
            # Filter out dynamic classes
            static_classes = [
                cls for cls in classes if not re.search(r"[0-9_]{2,}", cls)
            ]
            if static_classes:
                selector += "." + ".".join(static_classes)

        # Add data attributes for better specificity
        data_attrs = [attr for attr in element.attrs.keys() if attr.startswith("data-")]
        for attr in data_attrs:
            if element.get(attr):
                selector += f'[{attr}="{element[attr]}"]'
                break

        return selector

    def find_best_selectors(
        self, html_content: str, target_elements: List[str]
    ) -> Dict[str, str]:
        """
        Find the best CSS selectors for target elements.

        Args:
            html_content: HTML content to analyze
            target_elements: List of element types to find

        Returns:
            Dictionary mapping element types to their best selectors
        """
        soup = BeautifulSoup(html_content, "html.parser")
        best_selectors = {}

        for element_type in target_elements:
            selector = self._find_best_selector_for_type(soup, element_type)
            if selector:
                best_selectors[element_type] = selector

        return best_selectors

    def _find_best_selector_for_type(
        self, soup: BeautifulSoup, element_type: str
    ) -> str:
        """
        Find the best selector for a specific element type.

        Args:
            soup: BeautifulSoup object
            element_type: Type of element to find

        Returns:
            Best CSS selector for the element type
        """
        # Define search strategies for different element types
        strategies = {
            "product_containers": [
                ("div", {"class": re.compile(r"product|item|card|listing", re.I)}),
                ("article", {"class": re.compile(r"product|item|card|listing", re.I)}),
                ("section", {"class": re.compile(r"product|item|card|listing", re.I)}),
            ],
            "product_titles": [
                ("h1", {"class": re.compile(r"title|name|product", re.I)}),
                ("h2", {"class": re.compile(r"title|name|product", re.I)}),
                ("h3", {"class": re.compile(r"title|name|product", re.I)}),
                ("span", {"class": re.compile(r"title|name|product", re.I)}),
                ("div", {"class": re.compile(r"title|name|product", re.I)}),
            ],
            "product_prices": [
                ("span", {"class": re.compile(r"price|cost|amount", re.I)}),
                ("div", {"class": re.compile(r"price|cost|amount", re.I)}),
                ("p", {"class": re.compile(r"price|cost|amount", re.I)}),
            ],
            "product_images": [
                ("img", {"src": True}),
                ("img", {"class": re.compile(r"product|item|card", re.I)}),
            ],
            "product_links": [
                ("a", {"href": True, "class": re.compile(r"product|item|card", re.I)}),
                ("a", {"href": re.compile(r"product|item|detail", re.I)}),
            ],
        }

        if element_type not in strategies:
            return ""

        # Try each strategy and score the results
        best_selector = ""
        best_score = 0

        for tag, attrs in strategies[element_type]:
            elements = soup.find_all(tag, attrs)

            for element in elements:
                selector = self._generate_element_selector(element)
                if not selector:
                    continue

                # Score the selector based on specificity and reliability
                score = self._score_selector(selector, element)

                if score > best_score:
                    best_score = score
                    best_selector = selector

        return best_selector

    def _score_selector(self, selector: str, element: Tag) -> int:
        """
        Score a CSS selector based on its specificity and reliability.

        Args:
            selector: CSS selector string
            element: BeautifulSoup Tag element

        Returns:
            Score (higher is better)
        """
        score = 0

        # Base score for having a selector
        score += 10

        # Bonus for ID selectors (highest specificity)
        if selector.startswith("#"):
            score += 50

        # Bonus for class selectors
        if "." in selector:
            score += 20

        # Bonus for data attributes
        if "[data-" in selector:
            score += 30

        # Penalty for very generic selectors
        if selector in ["div", "span", "p", "a", "img"]:
            score -= 20

        # Bonus for semantic tag names
        semantic_tags = ["article", "section", "header", "footer", "nav", "main"]
        if any(tag in selector for tag in semantic_tags):
            score += 15

        # Bonus for having text content (indicates it's not empty)
        if element.get_text(strip=True):
            score += 10

        return score

    def adapt_to_site(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Adapt selectors to a specific site by analyzing its structure.

        Args:
            url: Website URL
            html_content: HTML content of the page

        Returns:
            Dictionary containing adapted selectors and site information
        """
        site_type = self.detect_site_type(url, html_content)

        # Generate base selectors
        selectors = self.generate_selectors(html_content, site_type)

        # Find best selectors for common elements
        target_elements = [
            "product_containers",
            "product_titles",
            "product_prices",
            "product_images",
            "product_links",
        ]
        best_selectors = self.find_best_selectors(html_content, target_elements)

        # Cache the results for this site
        domain = urlparse(url).netloc
        self.site_cache[domain] = {
            "site_type": site_type,
            "selectors": selectors,
            "best_selectors": best_selectors,
            "url": url,
        }

        return {
            "site_type": site_type,
            "domain": domain,
            "selectors": selectors,
            "best_selectors": best_selectors,
            "confidence": self._calculate_confidence(html_content, best_selectors),
        }

    def _calculate_confidence(
        self, html_content: str, selectors: Dict[str, str]
    ) -> float:
        """
        Calculate confidence level for the generated selectors.

        Args:
            html_content: HTML content
            selectors: Dictionary of selectors

        Returns:
            Confidence score between 0 and 1
        """
        soup = BeautifulSoup(html_content, "html.parser")
        total_score = 0
        max_score = len(selectors) * 100

        for element_type, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    # Score based on number of elements found
                    element_count = len(elements)
                    if element_count > 0:
                        total_score += min(100, element_count * 10)
                else:
                    total_score += 0
            except Exception:
                total_score += 0

        return total_score / max_score if max_score > 0 else 0

    def get_cached_selectors(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached selectors for a site if available.

        Args:
            url: Website URL

        Returns:
            Cached selector data or None if not found
        """
        domain = urlparse(url).netloc
        return self.site_cache.get(domain)

    def clear_cache(self) -> None:
        """Clear the site selector cache."""
        self.site_cache.clear()
