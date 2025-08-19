#!/usr/bin/env python3
"""
Data Enricher - Advanced data processing, cleaning, and enrichment for scraped data.
"""
import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
from urllib.parse import urlparse


@dataclass
class EnrichmentResult:
    """Result of data enrichment process."""

    original_data: List[Dict[str, Any]]
    enriched_data: List[Dict[str, Any]]
    enrichment_stats: Dict[str, Any]
    quality_score: float
    processing_time: float


class DataEnricher:
    """
    Advanced data processing and enrichment system.
    Cleans, normalizes, and enhances scraped data with additional insights.
    """

    def __init__(self):
        self.currency_symbols = {
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "₺": "TRY",
            "₹": "INR",
            "₽": "RUB",
            "₩": "KRW",
            "₪": "ILS",
            "₦": "NGN",
        }

        self.price_patterns = [
            r"[\$€£¥₺₹₽₩₪₦]\s*([\d,]+\.?\d*)",
            r"([\d,]+\.?\d*)\s*[\$€£¥₺₹₽₩₪₦]",
            r"([\d,]+\.?\d*)\s*(?:TL|USD|EUR|GBP|JPY|TRY|INR|RUB|KRW|ILS|NGN)",
            r"(?:TL|USD|EUR|GBP|JPY|TRY|INR|RUB|KRW|ILS|NGN)\s*([\d,]+\.?\d*)",
        ]

        self.phone_patterns = [
            r"\+?[\d\s\-\(\)]{10,}",
            r"[\d\s\-\(\)]{10,}",
            r"\+90\s*[\d\s\-\(\)]{10,}",  # Turkish format
            r"\+1\s*[\d\s\-\(\)]{10,}",  # US format
        ]

        self.email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Common product categories for classification
        self.product_categories = {
            "electronics": [
                "phone",
                "laptop",
                "computer",
                "tablet",
                "tv",
                "camera",
                "headphone",
            ],
            "automotive": ["car", "vehicle", "auto", "motorcycle", "truck", "suv"],
            "fashion": [
                "shirt",
                "dress",
                "shoe",
                "bag",
                "watch",
                "jewelry",
                "clothing",
            ],
            "home": ["furniture", "appliance", "kitchen", "bedroom", "living room"],
            "sports": ["bike", "bicycle", "fitness", "gym", "sport", "exercise"],
            "books": ["book", "novel", "textbook", "magazine", "publication"],
            "toys": ["toy", "game", "play", "children", "kids"],
        }

    def enrich_data(
        self, data: List[Dict[str, Any]], options: Dict[str, Any] = None
    ) -> EnrichmentResult:
        """
        Main enrichment function that processes and enhances scraped data.

        Args:
            data: List of scraped data dictionaries
            options: Enrichment options (price_normalization, deduplication, etc.)

        Returns:
            EnrichmentResult with processed data and statistics
        """
        start_time = datetime.now()

        if not options:
            options = {
                "price_normalization": True,
                "deduplication": True,
                "category_classification": True,
                "contact_extraction": True,
                "url_validation": True,
                "quality_scoring": True,
                "outlier_detection": True,
            }

        original_data = data.copy()
        enriched_data = []

        # Step 1: Basic cleaning
        cleaned_data = self._clean_data(data)

        # Step 2: Price normalization
        if options.get("price_normalization"):
            cleaned_data = self._normalize_prices(cleaned_data)

        # Step 3: Deduplication
        if options.get("deduplication"):
            cleaned_data = self._deduplicate_data(cleaned_data)

        # Step 4: Category classification
        if options.get("category_classification"):
            cleaned_data = self._classify_categories(cleaned_data)

        # Step 5: Contact extraction
        if options.get("contact_extraction"):
            cleaned_data = self._extract_contacts(cleaned_data)

        # Step 6: URL validation and enhancement
        if options.get("url_validation"):
            cleaned_data = self._validate_urls(cleaned_data)

        # Step 7: Quality scoring
        if options.get("quality_scoring"):
            cleaned_data = self._add_quality_scores(cleaned_data)

        # Step 8: Outlier detection
        if options.get("outlier_detection"):
            cleaned_data = self._detect_outliers(cleaned_data)

        # Step 9: Add metadata
        enriched_data = self._add_metadata(cleaned_data)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Generate enrichment statistics
        enrichment_stats = self._generate_enrichment_stats(
            original_data, enriched_data, processing_time
        )

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(enriched_data)

        return EnrichmentResult(
            original_data=original_data,
            enriched_data=enriched_data,
            enrichment_stats=enrichment_stats,
            quality_score=quality_score,
            processing_time=processing_time,
        )

    def _clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize basic data fields."""
        cleaned_data = []

        for item in data:
            cleaned_item = {}

            for key, value in item.items():
                if isinstance(value, str):
                    # Remove extra whitespace
                    cleaned_value = re.sub(r"\s+", " ", value.strip())
                    # Remove HTML tags
                    cleaned_value = re.sub(r"<[^>]+>", "", cleaned_value)
                    # Remove special characters that might cause issues
                    cleaned_value = re.sub(
                        r"[^\w\s\-\.\,\$€£¥₺₹₽₩₪₦@]", "", cleaned_value
                    )
                    cleaned_item[key] = cleaned_value
                else:
                    cleaned_item[key] = value

            # Remove items with empty required fields
            if cleaned_item.get("title") or cleaned_item.get("name"):
                cleaned_data.append(cleaned_item)

        return cleaned_data

    def _normalize_prices(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and normalize price information."""
        for item in data:
            # Look for price in various fields
            price_fields = ["price", "cost", "amount", "value", "title", "description"]
            extracted_price = None
            currency = "USD"

            for field in price_fields:
                if field in item and item[field]:
                    price_match = self._extract_price(item[field])
                    if price_match:
                        extracted_price = price_match["amount"]
                        currency = price_match["currency"]
                        break

            if extracted_price:
                item["normalized_price"] = extracted_price
                item["currency"] = currency
                item["price_confidence"] = self._calculate_price_confidence(item)

        return data

    def _extract_price(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract price and currency from text."""
        if not text:
            return None

        for pattern in self.price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    amount = float(amount_str)

                    # Determine currency
                    currency = "USD"  # Default
                    for symbol, curr in self.currency_symbols.items():
                        if symbol in text:
                            currency = curr
                            break

                    return {
                        "amount": amount,
                        "currency": currency,
                        "original_text": match.group(0),
                    }
                except ValueError:
                    continue

        return None

    def _deduplicate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entries based on similarity."""
        if not data:
            return data

        # Create a DataFrame for easier processing
        df = pd.DataFrame(data)

        # Create similarity groups based on title/name
        title_field = "title" if "title" in df.columns else "name"
        if title_field in df.columns:
            # Simple deduplication based on exact title match
            df = df.drop_duplicates(subset=[title_field], keep="first")

            # Advanced deduplication based on similarity (if needed)
            # This could use fuzzy matching for more sophisticated deduplication

        return df.to_dict("records")

    def _classify_categories(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify items into product categories."""
        for item in data:
            # Combine title and description for classification
            text = " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("name", "")),
                    str(item.get("description", "")),
                ]
            ).lower()

            category_scores = {}
            for category, keywords in self.product_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    category_scores[category] = score

            if category_scores:
                # Get the category with highest score
                best_category = max(category_scores, key=category_scores.get)
                item["category"] = best_category
                item["category_confidence"] = category_scores[best_category] / len(
                    self.product_categories[best_category]
                )
            else:
                item["category"] = "other"
                item["category_confidence"] = 0.0

        return data

    def _extract_contacts(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract contact information from text fields."""
        for item in data:
            # Combine all text fields
            text = " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("description", "")),
                    str(item.get("contact_info", "")),
                ]
            )

            # Extract phone numbers
            phones = []
            for pattern in self.phone_patterns:
                matches = re.findall(pattern, text)
                phones.extend(matches)

            # Extract emails
            emails = re.findall(self.email_pattern, text)

            if phones:
                item["phone_numbers"] = list(set(phones))  # Remove duplicates
            if emails:
                item["email_addresses"] = list(set(emails))  # Remove duplicates

        return data

    def _validate_urls(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and enhance URL information."""
        for item in data:
            if "url" in item and item["url"]:
                try:
                    parsed_url = urlparse(item["url"])
                    item["domain"] = parsed_url.netloc
                    item["url_valid"] = True

                    # Add protocol if missing
                    if not parsed_url.scheme:
                        item["url"] = "https://" + item["url"]

                except Exception:
                    item["url_valid"] = False
                    item["domain"] = None

        return data

    def _add_quality_scores(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add quality scores to each item."""
        for item in data:
            score = 0.0
            max_score = 100.0

            # Title/Name quality (30 points)
            title = item.get("title") or item.get("name", "")
            if title:
                score += min(30, len(title) * 0.5)  # Longer titles get more points

            # Price quality (25 points)
            if "normalized_price" in item:
                score += 25

            # Description quality (20 points)
            description = item.get("description", "")
            if description:
                score += min(20, len(description) * 0.1)

            # Image quality (15 points)
            if item.get("image_url") or item.get("image"):
                score += 15

            # Contact information (10 points)
            if item.get("phone_numbers") or item.get("email_addresses"):
                score += 10

            item["quality_score"] = score
            item["quality_percentage"] = (score / max_score) * 100

        return data

    def _detect_outliers(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect price outliers using statistical methods."""
        if not data or len(data) < 3:
            return data

        # Extract prices for outlier detection
        prices = []
        for item in data:
            if "normalized_price" in item:
                prices.append(item["normalized_price"])

        if len(prices) < 3:
            return data

        # Calculate statistics
        prices_array = np.array(prices)
        mean_price = np.mean(prices_array)
        std_price = np.std(prices_array)

        # Mark outliers (prices more than 2 standard deviations from mean)
        for item in data:
            if "normalized_price" in item:
                price = item["normalized_price"]
                z_score = abs(price - mean_price) / std_price if std_price > 0 else 0
                item["is_price_outlier"] = z_score > 2
                item["price_z_score"] = z_score

        return data

    def _add_metadata(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to each item."""
        for item in data:
            item["enrichment_timestamp"] = datetime.now().isoformat()
            item["data_version"] = "1.0"

            # Add word count for text fields
            title = item.get("title") or item.get("name", "")
            description = item.get("description", "")

            item["title_word_count"] = len(title.split())
            item["description_word_count"] = len(description.split())

        return data

    def _calculate_price_confidence(self, item: Dict[str, Any]) -> float:
        """Calculate confidence in extracted price."""
        confidence = 0.5  # Base confidence

        # Higher confidence if price is in dedicated price field
        if "price" in item and item["price"]:
            confidence += 0.3

        # Higher confidence for reasonable price ranges
        if "normalized_price" in item:
            price = item["normalized_price"]
            if 0 < price < 1000000:  # Reasonable range
                confidence += 0.2

        return min(1.0, confidence)

    def _generate_enrichment_stats(
        self,
        original_data: List[Dict[str, Any]],
        enriched_data: List[Dict[str, Any]],
        processing_time: float,
    ) -> Dict[str, Any]:
        """Generate comprehensive enrichment statistics."""
        stats = {
            "original_count": len(original_data),
            "enriched_count": len(enriched_data),
            "processing_time_seconds": processing_time,
            "data_loss_percentage": 0,
            "price_extraction_rate": 0,
            "category_classification_rate": 0,
            "contact_extraction_rate": 0,
            "average_quality_score": 0,
        }

        if original_data:
            stats["data_loss_percentage"] = (
                (len(original_data) - len(enriched_data)) / len(original_data) * 100
            )

        if enriched_data:
            # Calculate extraction rates
            prices_extracted = sum(
                1 for item in enriched_data if "normalized_price" in item
            )
            categories_assigned = sum(1 for item in enriched_data if "category" in item)
            contacts_extracted = sum(
                1
                for item in enriched_data
                if "phone_numbers" in item or "email_addresses" in item
            )
            quality_scores = [item.get("quality_score", 0) for item in enriched_data]

            stats["price_extraction_rate"] = (
                prices_extracted / len(enriched_data)
            ) * 100
            stats["category_classification_rate"] = (
                categories_assigned / len(enriched_data)
            ) * 100
            stats["contact_extraction_rate"] = (
                contacts_extracted / len(enriched_data)
            ) * 100
            stats["average_quality_score"] = (
                np.mean(quality_scores) if quality_scores else 0
            )

        return stats

    def _calculate_quality_score(self, data: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score for the dataset."""
        if not data:
            return 0.0

        quality_scores = [item.get("quality_score", 0) for item in data]
        return np.mean(quality_scores)

    def export_enriched_data(
        self, result: EnrichmentResult, format: str = "json", filename: str = None
    ) -> str:
        """Export enriched data to various formats."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enriched_data_{timestamp}.{format}"

        if format.lower() == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "enrichment_stats": result.enrichment_stats,
                        "quality_score": result.quality_score,
                        "processing_time": result.processing_time,
                        "data": result.enriched_data,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

        elif format.lower() == "csv":
            df = pd.DataFrame(result.enriched_data)
            df.to_csv(filename, index=False, encoding="utf-8")

        elif format.lower() == "excel":
            df = pd.DataFrame(result.enriched_data)
            with pd.ExcelWriter(filename, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Enriched Data", index=False)

                # Add stats sheet
                stats_df = pd.DataFrame([result.enrichment_stats])
                stats_df.to_excel(writer, sheet_name="Enrichment Stats", index=False)

        return filename
