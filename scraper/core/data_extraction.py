#!/usr/bin/env python3
"""
Data extraction module for the scraper.

This module handles extracting data from HTML content using various selectors and methods.
"""

import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from scraper.logging_manager.logging_manager import log_message


class DataExtractor:
    """
    Handles data extraction from HTML content using various methods.
    """

    def __init__(self, universal_extractor):
        """
        Initialize the data extractor.

        Args:
            universal_extractor: Universal extractor instance
        """
        self.universal_extractor = universal_extractor

    def extract_data(self, html: str, site_profile=None) -> List[Dict]:
        """
        Extract data from HTML content using appropriate method.

        Args:
            html: HTML content to extract from
            site_profile: Site profile for targeted extraction

        Returns:
            list: Extracted data items
        """
        try:
            if site_profile and site_profile.selectors:
                # Use smart selectors if available
                return self._extract_with_smart_selectors(html, site_profile)
            else:
                # Use default extraction method
                return self._extract_with_default_selectors(html)

        except Exception as e:
            log_message("ERROR", f"Error extracting data: {e}")
            return []

    def _extract_with_smart_selectors(self, html: str, site_profile) -> List[Dict]:
        """
        Extract data using smart selectors from site profile.

        Args:
            html: HTML content
            site_profile: Site profile with selectors

        Returns:
            list: Extracted data items
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            items = []

            # Get container selector
            container_selector = site_profile.selectors.get(
                "product_container", ".item, .product, .listing"
            )
            containers = soup.select(container_selector)

            log_message(
                "INFO",
                f"Found {len(containers)} containers with selector: {container_selector}",
            )

            for container in containers:
                item = {}

                # Extract each field using selectors
                for field, selector in site_profile.selectors.items():
                    if field == "product_container":
                        continue

                    element = container.select_one(selector)
                    if element:
                        item[field] = self._clean_text(element.get_text(strip=True))

                        # Extract additional attributes
                        if field == "link" and element.get("href"):
                            item["url"] = element.get("href")
                        elif field == "image" and element.get("src"):
                            item["image_url"] = element.get("src")

                if item:
                    items.append(item)

            log_message("INFO", f"Extracted {len(items)} items using smart selectors")
            return items

        except Exception as e:
            log_message("ERROR", f"Error with smart selectors: {e}")
            return []

    def _extract_with_default_selectors(self, html: str) -> List[Dict]:
        """
        Extract data using default selectors when site-specific ones are not available.

        Args:
            html: HTML content

        Returns:
            list: Extracted data items
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            items = []

            # Common selectors for different types of content
            common_selectors = [
                ".product",
                ".item",
                ".listing",
                ".card",
                ".post",
                ".article",
                ".entry",
                ".result",
                ".offer",
            ]

            for selector in common_selectors:
                containers = soup.select(selector)
                if containers:
                    log_message(
                        "INFO",
                        f"Found {len(containers)} items with selector: {selector}",
                    )

                    for container in containers:
                        item = self._extract_item_from_container(container)
                        if item:
                            items.append(item)

                    break  # Use first successful selector

            if not items:
                # Try to extract any structured data
                items = self._extract_structured_data(soup)

            log_message("INFO", f"Extracted {len(items)} items using default selectors")
            return items

        except Exception as e:
            log_message("ERROR", f"Error with default selectors: {e}")
            return []

    def _extract_item_from_container(self, container) -> Optional[Dict]:
        """
        Extract data from a single container element.

        Args:
            container: BeautifulSoup element

        Returns:
            dict: Extracted item data or None
        """
        try:
            item = {}

            # Try to find title
            title_selectors = ["h1", "h2", "h3", ".title", ".name", ".heading"]
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    item["title"] = self._clean_text(title_elem.get_text(strip=True))
                    break

            # Try to find price
            price_selectors = [".price", ".cost", ".amount", "[class*='price']"]
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    item["price"] = self._clean_text(price_elem.get_text(strip=True))
                    break

            # Try to find description
            desc_selectors = [".description", ".summary", ".content", "p"]
            for selector in desc_selectors:
                desc_elem = container.select_one(selector)
                if desc_elem:
                    item["description"] = self._clean_text(
                        desc_elem.get_text(strip=True)
                    )
                    break

            # Try to find link
            link_elem = container.select_one("a")
            if link_elem and link_elem.get("href"):
                item["url"] = link_elem.get("href")

            # Try to find image
            img_elem = container.select_one("img")
            if img_elem and img_elem.get("src"):
                item["image_url"] = img_elem.get("src")

            return item if item else None

        except Exception as e:
            log_message("ERROR", f"Error extracting item from container: {e}")
            return None

    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract structured data from the page.

        Args:
            soup: BeautifulSoup object

        Returns:
            list: Extracted structured data
        """
        items = []

        try:
            # Look for JSON-LD structured data
            json_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_scripts:
                try:
                    import json

                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        items.append(data)
                    elif isinstance(data, list):
                        items.extend(data)
                except:
                    continue

            # Look for microdata
            microdata_items = soup.find_all(attrs={"itemscope": True})
            for item in microdata_items:
                item_data = {}
                properties = item.find_all(attrs={"itemprop": True})
                for prop in properties:
                    key = prop.get("itemprop")
                    value = (
                        prop.get_text(strip=True)
                        if prop.get_text(strip=True)
                        else prop.get("content")
                    )
                    if key and value:
                        item_data[key] = value

                if item_data:
                    items.append(item_data)

        except Exception as e:
            log_message("ERROR", f"Error extracting structured data: {e}")

        return items

    def _extract_sahibinden_data(self, html: str) -> List[Dict]:
        """
        Extract data specifically for sahibinden.com.

        Args:
            html: HTML content

        Returns:
            list: Extracted sahibinden data
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            items = []

            # Sahibinden-specific selectors
            containers = soup.select(".classified-item")

            for container in containers:
                item = {}

                # Title
                title_elem = container.select_one(".classified-title")
                if title_elem:
                    item["title"] = self._clean_text(title_elem.get_text(strip=True))

                    # Link
                    link_elem = title_elem.select_one("a")
                    if link_elem and link_elem.get("href"):
                        item["url"] = link_elem.get("href")

                # Price
                price_elem = container.select_one(".classified-price")
                if price_elem:
                    item["price"] = self._clean_text(price_elem.get_text(strip=True))

                # Location
                location_elem = container.select_one(".classified-location")
                if location_elem:
                    item["location"] = self._clean_text(
                        location_elem.get_text(strip=True)
                    )

                # Description
                desc_elem = container.select_one(".classified-description")
                if desc_elem:
                    item["description"] = self._clean_text(
                        desc_elem.get_text(strip=True)
                    )

                # Image
                img_elem = container.select_one(".classified-image img")
                if img_elem and img_elem.get("src"):
                    item["image_url"] = img_elem.get("src")

                if item:
                    items.append(item)

            log_message("INFO", f"Extracted {len(items)} sahibinden items")
            return items

        except Exception as e:
            log_message("ERROR", f"Error extracting sahibinden data: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw text to clean

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?@#$%&*()+=/:;<>"\'\\]', "", text)

        return text

    def extract_with_adaptive_config(self, html: str, config: Dict) -> List[Dict]:
        """
        Extract data using adaptive configuration.

        Args:
            html: HTML content
            config: Adaptive configuration

        Returns:
            list: Extracted data items
        """
        try:
            # This would use the adaptive config manager to dynamically
            # adjust extraction strategies based on success rates
            log_message("INFO", "Using adaptive configuration for extraction")

            # For now, use default extraction
            return self._extract_with_default_selectors(html)

        except Exception as e:
            log_message("ERROR", f"Error with adaptive extraction: {e}")
            return []
