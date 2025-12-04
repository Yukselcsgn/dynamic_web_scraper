#!/usr/bin/env python3
# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Universal Data Extractor - Works with any website automatically
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup


@dataclass
class ExtractionResult:
    """Result of data extraction attempt."""

    success: bool
    data: List[Dict[str, Any]]
    selectors_used: Dict[str, str]
    confidence: float
    method: str
    error_message: Optional[str] = None


class UniversalExtractor:
    """
    Universal data extractor that automatically adapts to any website structure.
    Uses multiple strategies to find and extract product/listing data.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Common patterns for different types of content
        self.content_patterns = {
            "product": {
                "indicators": [
                    "product",
                    "item",
                    "goods",
                    "merchandise",
                    "listing",
                    "ad",
                ],
                "price_patterns": [
                    r"[\$€£¥₺]\s*\d+[\.,]?\d*",
                    r"\d+[\.,]?\d*\s*[\$€£¥₺]",
                    r"price\s*:?\s*[\$€£¥₺]?\s*\d+",
                    r"cost\s*:?\s*[\$€£¥₺]?\s*\d+",
                ],
                "title_patterns": [r"title", r"name", r"heading", r"product", r"item"],
            },
            "classified": {
                "indicators": [
                    "classified",
                    "listing",
                    "ad",
                    "advertisement",
                    "posting",
                ],
                "price_patterns": [
                    r"[\$€£¥₺]\s*\d+[\.,]?\d*",
                    r"\d+[\.,]?\d*\s*[\$€£¥₺]",
                    r"price\s*:?\s*[\$€£¥₺]?\s*\d+",
                    r"asking\s*:?\s*[\$€£¥₺]?\s*\d+",
                ],
                "title_patterns": [r"title", r"subject", r"heading", r"listing", r"ad"],
            },
            "news": {
                "indicators": ["article", "news", "story", "post", "blog"],
                "title_patterns": [r"headline", r"title", r"subject", r"article"],
            },
        }

        # Multi-level selector strategies
        self.selector_strategies = [
            self._strategy_specific_selectors,
            self._strategy_semantic_analysis,
            self._strategy_structure_analysis,
            self._strategy_pattern_matching,
            self._strategy_fallback_generic,
        ]

    def extract_data(self, html_content: str, url: str = None) -> ExtractionResult:
        """
        Extract data from HTML content using multiple strategies.

        Args:
            html_content: HTML content to analyze
            url: Optional URL for context

        Returns:
            ExtractionResult with extracted data and metadata
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Try each strategy until one succeeds
            for i, strategy in enumerate(self.selector_strategies):
                try:
                    result = strategy(soup, url)
                    if result.success and result.data:
                        result.method = f"strategy_{i+1}"
                        self.logger.info(
                            f"Success with strategy {i+1}: {len(result.data)} items extracted"
                        )
                        return result
                except Exception as e:
                    self.logger.warning(f"Strategy {i+1} failed: {e}")
                    continue

            # If all strategies fail, return empty result
            return ExtractionResult(
                success=False,
                data=[],
                selectors_used={},
                confidence=0.0,
                method="none",
                error_message="All extraction strategies failed",
            )

        except Exception as e:
            return ExtractionResult(
                success=False,
                data=[],
                selectors_used={},
                confidence=0.0,
                method="error",
                error_message=str(e),
            )

    def _strategy_specific_selectors(
        self, soup: BeautifulSoup, url: str = None
    ) -> ExtractionResult:
        """Strategy 1: Use known specific selectors for popular sites."""
        domain = urlparse(url).netloc.lower() if url else ""

        # Known selectors for popular sites
        known_selectors = {
            "amazon.com": {
                "container": "div[data-component-type='s-search-result']",
                "title": "h2 a span",
                "price": ".a-price-whole",
                "image": "img[data-image-latency]",
                "link": "h2 a",
            },
            "ebay.com": {
                "container": ".s-item",
                "title": ".s-item__title",
                "price": ".s-item__price",
                "image": ".s-item__image img",
                "link": ".s-item__link",
            },
            "sahibinden.com": {
                "container": "tr.searchResultsItem",
                "title": "td.searchResultsTitleValue a",
                "price": "td.searchResultsPriceValue",
                "image": "td.searchResultsImageValue img",
                "link": "td.searchResultsTitleValue a",
            },
            "hepsiburada.com": {
                "container": ".productListContent-item",
                "title": ".productListContent-productName",
                "price": ".price-value",
                "image": ".productListContent-img img",
                "link": ".productListContent-productName",
            },
            "trendyol.com": {
                "container": ".p-card-wrppr",
                "title": ".prdct-desc-cntnr-name",
                "price": ".prc-box-dscntd",
                "image": ".p-card-img img",
                "link": ".p-card-wrppr a",
            },
        }

        # Check if we have known selectors for this domain
        for site_domain, selectors in known_selectors.items():
            if site_domain in domain:
                return self._extract_with_selectors(
                    soup, selectors, f"known_{site_domain}"
                )

        # Return failure to try next strategy
        return ExtractionResult(
            success=False, data=[], selectors_used={}, confidence=0.0, method=""
        )

    def _strategy_semantic_analysis(
        self, soup: BeautifulSoup, url: str = None
    ) -> ExtractionResult:
        """Strategy 2: Analyze page semantics to find content containers."""
        try:
            # Detect content type
            content_type = self._detect_content_type(soup, url)

            # Find containers based on content type
            containers = self._find_semantic_containers(soup, content_type)

            if not containers:
                return ExtractionResult(
                    success=False, data=[], selectors_used={}, confidence=0.0, method=""
                )

            # Extract data from containers
            data = []
            selectors_used = {}

            for container in containers:
                item_data = self._extract_item_from_container(container, content_type)
                if item_data:
                    data.append(item_data)

            if data:
                selectors_used = {
                    "container": f"semantic_{content_type}",
                    "method": "semantic_analysis",
                }
                return ExtractionResult(
                    success=True,
                    data=data,
                    selectors_used=selectors_used,
                    confidence=0.7,
                    method="semantic_analysis",
                )

            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {e}")
            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

    def _strategy_structure_analysis(
        self, soup: BeautifulSoup, url: str = None
    ) -> ExtractionResult:
        """Strategy 3: Analyze HTML structure to find repeating patterns."""
        try:
            # Find repeating structures
            repeating_structures = self._find_repeating_structures(soup)

            if not repeating_structures:
                return ExtractionResult(
                    success=False, data=[], selectors_used={}, confidence=0.0, method=""
                )

            # Analyze the best structure
            best_structure = self._analyze_structure_quality(repeating_structures)

            if not best_structure:
                return ExtractionResult(
                    success=False, data=[], selectors_used={}, confidence=0.0, method=""
                )

            # Extract data using the best structure
            data = self._extract_from_structure(soup, best_structure)

            if data:
                return ExtractionResult(
                    success=True,
                    data=data,
                    selectors_used=best_structure,
                    confidence=0.6,
                    method="structure_analysis",
                )

            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

        except Exception as e:
            self.logger.error(f"Structure analysis failed: {e}")
            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

    def _strategy_pattern_matching(
        self, soup: BeautifulSoup, url: str = None
    ) -> ExtractionResult:
        """Strategy 4: Use pattern matching to find content."""
        try:
            # Look for price patterns
            price_elements = self._find_price_elements(soup)

            if not price_elements:
                return ExtractionResult(
                    success=False, data=[], selectors_used={}, confidence=0.0, method=""
                )

            # Group elements by their containers
            containers = self._group_elements_by_container(price_elements)

            # Extract data from each container
            data = []
            for container in containers:
                item_data = self._extract_from_price_container(container)
                if item_data:
                    data.append(item_data)

            if data:
                return ExtractionResult(
                    success=True,
                    data=data,
                    selectors_used={"method": "pattern_matching"},
                    confidence=0.5,
                    method="pattern_matching",
                )

            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

        except Exception as e:
            self.logger.error(f"Pattern matching failed: {e}")
            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

    def _strategy_fallback_generic(
        self, soup: BeautifulSoup, url: str = None
    ) -> ExtractionResult:
        """Strategy 5: Generic fallback using common patterns."""
        try:
            # Try generic selectors
            generic_selectors = {
                "container": "div, article, section, li, tr",
                "title": "h1, h2, h3, h4, .title, .name, [class*='title'], [class*='name']",
                "price": "[class*='price'], [class*='cost'], [data-price]",
                "image": "img",
                "link": "a",
            }

            return self._extract_with_selectors(
                soup, generic_selectors, "generic_fallback"
            )

        except Exception as e:
            self.logger.error(f"Generic fallback failed: {e}")
            return ExtractionResult(
                success=False, data=[], selectors_used={}, confidence=0.0, method=""
            )

    def _extract_with_selectors(
        self, soup: BeautifulSoup, selectors: Dict[str, str], method_name: str
    ) -> ExtractionResult:
        """Extract data using specific selectors."""
        try:
            containers = soup.select(selectors.get("container", "div"))

            if not containers:
                return ExtractionResult(
                    success=False,
                    data=[],
                    selectors_used=selectors,
                    confidence=0.0,
                    method="",
                )

            data = []
            for container in containers:
                item_data = {}

                # Extract title
                if "title" in selectors:
                    title_elem = container.select_one(selectors["title"])
                    if title_elem:
                        item_data["title"] = title_elem.get_text(strip=True)
                        if title_elem.name == "a":
                            item_data["url"] = title_elem.get("href", "")

                # Extract price
                if "price" in selectors:
                    price_elem = container.select_one(selectors["price"])
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if self._is_valid_price(price_text):
                            item_data["price"] = price_text

                # Extract image
                if "image" in selectors:
                    img_elem = container.select_one(selectors["image"])
                    if img_elem:
                        item_data["image_url"] = img_elem.get("src", "")

                # Extract link
                if "link" in selectors and "url" not in item_data:
                    link_elem = container.select_one(selectors["link"])
                    if link_elem:
                        item_data["url"] = link_elem.get("href", "")

                # Add metadata
                item_data["source_url"] = ""
                item_data["extraction_timestamp"] = datetime.now().isoformat()
                item_data["extraction_method"] = method_name

                # Only add if we have at least a title or price
                if item_data.get("title") or item_data.get("price"):
                    data.append(item_data)

            confidence = 0.8 if len(data) > 0 else 0.0
            return ExtractionResult(
                success=len(data) > 0,
                data=data,
                selectors_used=selectors,
                confidence=confidence,
                method=method_name,
            )

        except Exception as e:
            self.logger.error(f"Selector extraction failed: {e}")
            return ExtractionResult(
                success=False,
                data=[],
                selectors_used=selectors,
                confidence=0.0,
                method="",
            )

    def _detect_content_type(self, soup: BeautifulSoup, url: str = None) -> str:
        """Detect the type of content on the page."""
        text_content = soup.get_text().lower()
        domain = urlparse(url).netloc.lower() if url else ""

        # Check for e-commerce indicators
        ecommerce_indicators = [
            "add to cart",
            "buy now",
            "checkout",
            "shopping cart",
            "product",
        ]
        if any(indicator in text_content for indicator in ecommerce_indicators):
            return "product"

        # Check for classified indicators
        classified_indicators = [
            "for sale",
            "wanted",
            "contact seller",
            "classified",
            "listing",
        ]
        if any(indicator in text_content for indicator in classified_indicators):
            return "classified"

        # Check for news indicators
        news_indicators = ["article", "news", "published", "author", "read more"]
        if any(indicator in text_content for indicator in news_indicators):
            return "news"

        # Default to product
        return "product"

    def _find_semantic_containers(self, soup: BeautifulSoup, content_type: str) -> List:
        """Find containers based on semantic analysis."""
        containers = []

        # Look for common container patterns
        container_selectors = [
            "div[class*='product']",
            "div[class*='item']",
            "div[class*='listing']",
            "div[class*='card']",
            "article",
            "section",
            "li[class*='item']",
            "tr[class*='item']",
        ]

        for selector in container_selectors:
            found = soup.select(selector)
            if found and len(found) > 1:  # Multiple items suggest a list
                containers.extend(found)

        return containers

    def _extract_item_from_container(
        self, container, content_type: str
    ) -> Dict[str, Any]:
        """Extract data from a single container."""
        item_data = {}

        # Extract title
        title_selectors = [
            "h1",
            "h2",
            "h3",
            "h4",
            ".title",
            ".name",
            "[class*='title']",
            "[class*='name']",
        ]
        for selector in title_selectors:
            title_elem = container.select_one(selector)
            if title_elem:
                item_data["title"] = title_elem.get_text(strip=True)
                if title_elem.name == "a":
                    item_data["url"] = title_elem.get("href", "")
                break

        # Extract price
        price_elem = self._find_price_in_element(container)
        if price_elem:
            item_data["price"] = price_elem.get_text(strip=True)

        # Extract image
        img_elem = container.select_one("img")
        if img_elem:
            item_data["image_url"] = img_elem.get("src", "")

        # Extract link
        if "url" not in item_data:
            link_elem = container.select_one("a")
            if link_elem:
                item_data["url"] = link_elem.get("href", "")

        return item_data

    def _find_repeating_structures(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find repeating HTML structures that might contain data."""
        structures = []

        # Look for repeating div patterns
        all_divs = soup.find_all("div")
        class_counts = {}

        for div in all_divs:
            classes = div.get("class", [])
            if classes:
                class_key = " ".join(sorted(classes))
                class_counts[class_key] = class_counts.get(class_key, 0) + 1

        # Find classes that appear multiple times (likely containers)
        for class_key, count in class_counts.items():
            if count > 2:  # At least 3 items
                structures.append(
                    {
                        "selector": f"div.{'.'.join(class_key.split())}",
                        "count": count,
                        "type": "div_class",
                    }
                )

        # Look for repeating table rows
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) > 2:  # Header + at least 2 data rows
                structures.append(
                    {"selector": f"table tr", "count": len(rows), "type": "table_row"}
                )

        return structures

    def _analyze_structure_quality(
        self, structures: List[Dict[str, Any]]
    ) -> Optional[Dict[str, str]]:
        """Analyze which structure is most likely to contain the data we want."""
        if not structures:
            return None

        # Sort by count (more items = better)
        structures.sort(key=lambda x: x["count"], reverse=True)

        # Return the best structure
        best = structures[0]
        return {"container": best["selector"], "method": "structure_analysis"}

    def _extract_from_structure(
        self, soup: BeautifulSoup, structure: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Extract data using a detected structure."""
        containers = soup.select(structure["container"])
        data = []

        for container in containers:
            item_data = self._extract_item_from_container(container, "product")
            if item_data:
                data.append(item_data)

        return data

    def _find_price_elements(self, soup: BeautifulSoup) -> List:
        """Find elements that contain price information."""
        price_elements = []

        # Look for elements containing price patterns
        for pattern in self.content_patterns["product"]["price_patterns"]:
            elements = soup.find_all(text=re.compile(pattern, re.I))
            for elem in elements:
                if elem.parent:
                    price_elements.append(elem.parent)

        return price_elements

    def _group_elements_by_container(self, elements: List) -> List:
        """Group elements by their common containers."""
        containers = {}

        for elem in elements:
            # Find the nearest container
            container = elem
            while container and container.name != "body":
                container = container.parent
                if container:
                    container_id = id(container)
                    if container_id not in containers:
                        containers[container_id] = container

        return list(containers.values())

    def _extract_from_price_container(self, container) -> Dict[str, Any]:
        """Extract data from a container that contains price information."""
        item_data = {}

        # Find price
        price_elem = self._find_price_in_element(container)
        if price_elem:
            item_data["price"] = price_elem.get_text(strip=True)

        # Find title
        title_selectors = [
            "h1",
            "h2",
            "h3",
            "h4",
            ".title",
            ".name",
            "[class*='title']",
        ]
        for selector in title_selectors:
            title_elem = container.select_one(selector)
            if title_elem:
                item_data["title"] = title_elem.get_text(strip=True)
                break

        return item_data

    def _find_price_in_element(self, element) -> Optional:
        """Find price information within an element."""
        # Look for price patterns in text
        text = element.get_text()
        for pattern in self.content_patterns["product"]["price_patterns"]:
            if re.search(pattern, text, re.I):
                return element

        # Look for price in child elements
        price_selectors = ["[class*='price']", "[class*='cost']", "[data-price]"]
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                return price_elem

        return None

    def _is_valid_price(self, price_text: str) -> bool:
        """Check if text looks like a valid price."""
        if not price_text:
            return False

        # Check for price patterns
        for pattern in self.content_patterns["product"]["price_patterns"]:
            if re.search(pattern, price_text, re.I):
                return True

        return False

    def save_extraction_result(self, result: ExtractionResult, filename: str):
        """Save extraction result to a JSON file."""
        result_dict = {
            "success": result.success,
            "data": result.data,
            "selectors_used": result.selectors_used,
            "confidence": result.confidence,
            "method": result.method,
            "error_message": result.error_message,
            "timestamp": datetime.now().isoformat(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

    def generate_selector_report(
        self, html_content: str, url: str = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive report of all possible selectors."""
        soup = BeautifulSoup(html_content, "html.parser")

        report = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "strategies_tested": [],
            "recommendations": [],
        }

        # Test each strategy
        for i, strategy in enumerate(self.selector_strategies):
            try:
                result = strategy(soup, url)
                report["strategies_tested"].append(
                    {
                        "strategy": i + 1,
                        "method": result.method,
                        "success": result.success,
                        "confidence": result.confidence,
                        "data_count": len(result.data),
                        "selectors_used": result.selectors_used,
                    }
                )
            except Exception as e:
                report["strategies_tested"].append(
                    {
                        "strategy": i + 1,
                        "method": f"strategy_{i+1}",
                        "success": False,
                        "error": str(e),
                    }
                )

        # Generate recommendations
        successful_strategies = [s for s in report["strategies_tested"] if s["success"]]
        if successful_strategies:
            best_strategy = max(successful_strategies, key=lambda x: x["confidence"])
            report["recommendations"].append(
                {
                    "type": "best_strategy",
                    "strategy": best_strategy["strategy"],
                    "confidence": best_strategy["confidence"],
                    "selectors": best_strategy["selectors_used"],
                }
            )

        return report
