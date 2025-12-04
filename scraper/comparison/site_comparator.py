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
Site Comparison and Analysis Module

This module provides comprehensive comparative analysis capabilities for the Dynamic Web Scraper,
including cross-site price comparison, product matching, and best deal recommendations.
"""

import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

# Add the project root to the path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scraper.analytics import DataVisualizer, PriceAnalyzer, TimeSeriesAnalyzer
from scraper.logging_manager.logging_manager import log_message, setup_logging


@dataclass
class ProductMatch:
    """Represents a matched product across multiple sites."""

    product_id: str
    title: str
    category: str
    brand: Optional[str] = None
    model: Optional[str] = None
    confidence_score: float = 0.0
    sites: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.sites is None:
            self.sites = []


@dataclass
class PriceComparison:
    """Represents price comparison results for a product."""

    product_id: str
    title: str
    category: str
    best_price: float
    worst_price: float
    average_price: float
    price_range: float
    price_variance: float
    site_count: int
    price_distribution: Dict[str, float]
    recommendations: List[str]
    last_updated: datetime


@dataclass
class DealAnalysis:
    """Represents deal analysis results."""

    product_id: str
    title: str
    deal_score: float  # 0-100, higher is better
    deal_type: str  # 'excellent', 'good', 'fair', 'poor'
    savings_percentage: float
    price_difference: float
    best_site: str
    worst_site: str
    price_history: List[Dict[str, Any]]
    recommendations: List[str]


class SiteComparator:
    """
    Comprehensive site comparison and analysis system.
    """

    def __init__(self, data_directory: str = "data"):
        """
        Initialize the site comparator.

        Args:
            data_directory: Directory containing scraped data
        """
        self.data_directory = Path(data_directory)
        self.logger = logging.getLogger("SiteComparator")

        # Initialize analytics components
        self.visualizer = DataVisualizer(f"{data_directory}/visualizations")
        self.time_analyzer = TimeSeriesAnalyzer(f"{data_directory}/time_series")
        self.price_analyzer = PriceAnalyzer()

        # Create necessary directories
        self.data_directory.mkdir(parents=True, exist_ok=True)
        (self.data_directory / "comparisons").mkdir(exist_ok=True)

        # Product matching configuration
        self.title_similarity_threshold = 0.7
        self.category_match_weight = 0.3
        self.brand_match_weight = 0.4
        self.model_match_weight = 0.3

        # Deal analysis configuration
        self.excellent_deal_threshold = 0.25  # 25% savings
        self.good_deal_threshold = 0.15  # 15% savings
        self.fair_deal_threshold = 0.05  # 5% savings

        self.logger.info("Site comparator initialized")

    def load_comparison_data(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Load data for comparison analysis.

        Args:
            days_back: Number of days to look back

        Returns:
            List of data items for comparison
        """
        try:
            all_data = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Load all data files in the data directory
            data_files = list(self.data_directory.glob("*.json"))

            for file_path in data_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_data = json.load(f)

                    # Filter by date if timestamp is available
                    if file_data and isinstance(file_data, list) and len(file_data) > 0:
                        if "timestamp" in file_data[0]:
                            # Filter data by date
                            filtered_data = []
                            for item in file_data:
                                try:
                                    item_date = datetime.fromisoformat(
                                        item["timestamp"].replace("Z", "+00:00")
                                    )
                                    if item_date >= cutoff_date:
                                        filtered_data.append(item)
                                except:
                                    filtered_data.append(
                                        item
                                    )  # Include if date parsing fails
                            all_data.extend(filtered_data)
                        else:
                            all_data.extend(file_data)

                except Exception as e:
                    self.logger.warning(f"Error loading {file_path}: {e}")
                    continue

            self.logger.info(f"Loaded {len(all_data)} data items for comparison")
            return all_data

        except Exception as e:
            self.logger.error(f"Error loading comparison data: {e}")
            return []

    def load_data(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Load data for comparison analysis (alias for load_comparison_data).

        Args:
            days_back: Number of days to look back

        Returns:
            List of data items for comparison
        """
        return self.load_comparison_data(days_back)

    def match_products(self, data: List[Dict[str, Any]]) -> List[ProductMatch]:
        """
        Match products across different sites.

        Args:
            data: List of data items to match

        Returns:
            List of product matches
        """
        try:
            product_matches = []
            processed_products = set()

            for i, product1 in enumerate(data):
                if product1.get("id") in processed_products:
                    continue

                matches = [product1]
                processed_products.add(product1.get("id"))

                for j, product2 in enumerate(data[i + 1 :], i + 1):
                    if product2.get("id") in processed_products:
                        continue

                    if self._are_products_similar(product1, product2):
                        matches.append(product2)
                        processed_products.add(product2.get("id"))

                if len(matches) > 1:
                    product_match = ProductMatch(
                        product_id=product1.get("id", f"match_{len(product_matches)}"),
                        title=product1.get("title", ""),
                        category=product1.get("category", ""),
                        brand=product1.get("brand"),
                        model=product1.get("model"),
                        confidence_score=0.8,
                        sites=matches,
                    )
                    product_matches.append(product_match)

            self.logger.info(f"Found {len(product_matches)} product matches")
            return product_matches

        except Exception as e:
            self.logger.error(f"Error matching products: {e}")
            return []

    def compare_prices(
        self, product_matches: List[ProductMatch]
    ) -> List[PriceComparison]:
        """
        Compare prices for matched products.

        Args:
            product_matches: List of product matches

        Returns:
            List of price comparisons
        """
        try:
            price_comparisons = []

            for match in product_matches:
                prices = []
                for site in match.sites:
                    price = site.get("price")
                    if price and isinstance(price, (int, float)):
                        prices.append(price)

                if len(prices) > 1:
                    price_comparison = PriceComparison(
                        product_id=match.product_id,
                        title=match.title,
                        category=match.category,
                        best_price=min(prices),
                        worst_price=max(prices),
                        average_price=sum(prices) / len(prices),
                        price_range=max(prices) - min(prices),
                        price_variance=np.var(prices) if len(prices) > 1 else 0,
                        site_count=len(prices),
                        price_distribution={},
                        recommendations=[],
                        last_updated=datetime.now(),
                    )
                    price_comparisons.append(price_comparison)

            self.logger.info(f"Generated {len(price_comparisons)} price comparisons")
            return price_comparisons

        except Exception as e:
            self.logger.error(f"Error comparing prices: {e}")
            return []

    def analyze_deals(
        self, price_comparisons: List[PriceComparison]
    ) -> List[DealAnalysis]:
        """
        Analyze deals based on price comparisons.

        Args:
            price_comparisons: List of price comparisons

        Returns:
            List of deal analyses
        """
        try:
            deal_analyses = []

            for comparison in price_comparisons:
                savings_percentage = (
                    comparison.worst_price - comparison.best_price
                ) / comparison.worst_price

                if savings_percentage >= self.excellent_deal_threshold:
                    deal_type = "excellent"
                elif savings_percentage >= self.good_deal_threshold:
                    deal_type = "good"
                elif savings_percentage >= self.fair_deal_threshold:
                    deal_type = "fair"
                else:
                    deal_type = "poor"

                deal_analysis = DealAnalysis(
                    product_id=comparison.product_id,
                    title=comparison.title,
                    deal_score=min(100, savings_percentage * 100),
                    deal_type=deal_type,
                    savings_percentage=savings_percentage * 100,
                    price_difference=comparison.price_range,
                    best_site="",
                    worst_site="",
                    price_history=[],
                    recommendations=[],
                )
                deal_analyses.append(deal_analysis)

            self.logger.info(f"Generated {len(deal_analyses)} deal analyses")
            return deal_analyses

        except Exception as e:
            self.logger.error(f"Error analyzing deals: {e}")
            return []

    def generate_comparison_report(
        self,
        product_matches: List[ProductMatch],
        price_comparisons: List[PriceComparison],
        deal_analyses: List[DealAnalysis],
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive comparison report.

        Args:
            product_matches: List of product matches
            price_comparisons: List of price comparisons
            deal_analyses: List of deal analyses

        Returns:
            Comparison report
        """
        try:
            report = {
                "summary": {
                    "total_products": len(product_matches),
                    "total_comparisons": len(price_comparisons),
                    "total_deals": len(deal_analyses),
                    "excellent_deals": len(
                        [d for d in deal_analyses if d.deal_type == "excellent"]
                    ),
                    "good_deals": len(
                        [d for d in deal_analyses if d.deal_type == "good"]
                    ),
                    "generated_at": datetime.now().isoformat(),
                },
                "product_matches": [
                    self._product_match_to_dict(match) for match in product_matches
                ],
                "price_comparisons": [
                    self._price_comparison_to_dict(comp) for comp in price_comparisons
                ],
                "deal_analyses": [
                    self._deal_analysis_to_dict(deal) for deal in deal_analyses
                ],
            }

            self.logger.info("Generated comparison report")
            return report

        except Exception as e:
            self.logger.error(f"Error generating comparison report: {e}")
            return {}

    def get_intelligent_recommendations(
        self, deal_analyses: List[DealAnalysis]
    ) -> List[str]:
        """
        Generate intelligent recommendations based on deal analyses.

        Args:
            deal_analyses: List of deal analyses

        Returns:
            List of recommendations
        """
        try:
            recommendations = []

            excellent_deals = [d for d in deal_analyses if d.deal_type == "excellent"]
            if excellent_deals:
                recommendations.append(
                    f"Found {len(excellent_deals)} excellent deals with savings up to {max(d.savings_percentage for d in excellent_deals):.1f}%"
                )

            good_deals = [d for d in deal_analyses if d.deal_type == "good"]
            if good_deals:
                recommendations.append(
                    f"Found {len(good_deals)} good deals worth considering"
                )

            if not recommendations:
                recommendations.append("No significant deals found in current data")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def _are_products_similar(
        self, product1: Dict[str, Any], product2: Dict[str, Any]
    ) -> bool:
        """Check if two products are similar."""
        try:
            title1 = product1.get("title", "").lower()
            title2 = product2.get("title", "").lower()

            # Simple similarity check
            similarity = SequenceMatcher(None, title1, title2).ratio()
            return similarity > self.title_similarity_threshold

        except Exception as e:
            self.logger.error(f"Error checking product similarity: {e}")
            return False

    def _product_match_to_dict(self, match: ProductMatch) -> Dict[str, Any]:
        """Convert ProductMatch to dictionary."""
        return {
            "product_id": match.product_id,
            "title": match.title,
            "category": match.category,
            "brand": match.brand,
            "model": match.model,
            "confidence_score": match.confidence_score,
            "site_count": len(match.sites),
        }

    def _price_comparison_to_dict(self, comparison: PriceComparison) -> Dict[str, Any]:
        """Convert PriceComparison to dictionary."""
        return {
            "product_id": comparison.product_id,
            "title": comparison.title,
            "best_price": comparison.best_price,
            "worst_price": comparison.worst_price,
            "average_price": comparison.average_price,
            "price_range": comparison.price_range,
            "site_count": comparison.site_count,
        }

    def _deal_analysis_to_dict(self, deal: DealAnalysis) -> Dict[str, Any]:
        """Convert DealAnalysis to dictionary."""
        return {
            "product_id": deal.product_id,
            "title": deal.title,
            "deal_score": deal.deal_score,
            "deal_type": deal.deal_type,
            "savings_percentage": deal.savings_percentage,
        }

    def extract_product_features(
        self, title: str, category: str = None
    ) -> Dict[str, Any]:
        """
        Extract product features for matching.

        Args:
            title: Product title
            category: Product category

        Returns:
            Dictionary of extracted features
        """
        try:
            features = {
                "title_clean": self._clean_title(title),
                "words": set(self._clean_title(title).lower().split()),
                "brand": self._extract_brand(title),
                "model": self._extract_model(title),
                "category": category,
                "title_hash": hashlib.md5(title.lower().encode()).hexdigest(),
            }

            return features

        except Exception as e:
            self.logger.error(f"Error extracting product features: {e}")
            return {}

    def _clean_title(self, title: str) -> str:
        """Clean product title for better matching."""
        try:
            # Remove common noise words and characters
            title = re.sub(r"[^\w\s]", " ", title)
            title = re.sub(r"\s+", " ", title).strip()

            # Remove common noise words
            noise_words = {
                "new",
                "used",
                "refurbished",
                "original",
                "genuine",
                "authentic",
                "free",
                "shipping",
                "delivery",
                "warranty",
                "guarantee",
                "best",
                "top",
                "premium",
                "quality",
                "high",
                "low",
            }

            words = title.lower().split()
            cleaned_words = [
                word for word in words if word not in noise_words and len(word) > 2
            ]

            return " ".join(cleaned_words)

        except Exception as e:
            self.logger.error(f"Error cleaning title: {e}")
            return title

    def _extract_brand(self, title: str) -> Optional[str]:
        """Extract brand from product title."""
        try:
            # Common brand patterns
            brand_patterns = [
                r"\b(apple|samsung|sony|lg|nike|adidas|canon|nikon|dell|hp|lenovo|asus|acer|msi|razer)\b",
                r"\b(iphone|ipad|macbook|galaxy|playstation|xbox|switch)\b",
                r"\b(intel|amd|nvidia|qualcomm|mediatek)\b",
            ]

            title_lower = title.lower()
            for pattern in brand_patterns:
                match = re.search(pattern, title_lower)
                if match:
                    return match.group(1).title()

            return None

        except Exception as e:
            self.logger.error(f"Error extracting brand: {e}")
            return None

    def _extract_model(self, title: str) -> Optional[str]:
        """Extract model number from product title."""
        try:
            # Common model patterns
            model_patterns = [
                r"\b([A-Z]{1,3}\d{3,4}[A-Z]?)\b",  # iPhone 14, Galaxy S23
                r"\b(\d{4}[A-Z]?)\b",  # 2023, 2024
                r"\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b",  # XPS-13, ThinkPad-T14
                r"\b([A-Z]{1,3}\d{2,3}[A-Z]{1,2})\b",  # RTX4080, RX6700XT
            ]

            for pattern in model_patterns:
                match = re.search(pattern, title.upper())
                if match:
                    return match.group(1)

            return None

        except Exception as e:
            self.logger.error(f"Error extracting model: {e}")
            return None

    def calculate_similarity(
        self, features1: Dict[str, Any], features2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two product feature sets.

        Args:
            features1: Features of first product
            features2: Features of second product

        Returns:
            Similarity score (0-1)
        """
        try:
            if not features1 or not features2:
                return 0.0

            # Title similarity using sequence matcher
            title_sim = SequenceMatcher(
                None, features1.get("title_clean", ""), features2.get("title_clean", "")
            ).ratio()

            # Word overlap similarity
            words1 = features1.get("words", set())
            words2 = features2.get("words", set())

            if words1 and words2:
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                word_sim = intersection / union if union > 0 else 0.0
            else:
                word_sim = 0.0

            # Brand similarity
            brand1 = features1.get("brand")
            brand2 = features2.get("brand")
            brand_sim = 1.0 if brand1 and brand2 and brand1 == brand2 else 0.0

            # Model similarity
            model1 = features1.get("model")
            model2 = features2.get("model")
            model_sim = 1.0 if model1 and model2 and model1 == model2 else 0.0

            # Category similarity
            cat1 = features1.get("category")
            cat2 = features2.get("category")
            cat_sim = 1.0 if cat1 and cat2 and cat1 == cat2 else 0.0

            # Weighted combination
            similarity = (
                title_sim * 0.4
                + word_sim * 0.3
                + brand_sim * self.brand_match_weight
                + model_sim * self.model_match_weight
                + cat_sim * self.category_match_weight
            )

            return min(similarity, 1.0)

        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def match_products(self, data: List[Dict[str, Any]]) -> List[ProductMatch]:
        """
        Match similar products across different sites.

        Args:
            data: List of scraped data items

        Returns:
            List of matched product groups
        """
        try:
            if not data:
                return []

            # Extract features for all products
            products_with_features = []
            for item in data:
                features = self.extract_product_features(
                    item.get("title", ""), item.get("category")
                )
                if features:
                    products_with_features.append({"item": item, "features": features})

            # Group products by similarity
            matched_groups = []
            processed_indices = set()

            for i, product1 in enumerate(products_with_features):
                if i in processed_indices:
                    continue

                # Find similar products
                similar_products = [product1]
                processed_indices.add(i)

                for j, product2 in enumerate(products_with_features[i + 1 :], i + 1):
                    if j in processed_indices:
                        continue

                    similarity = self.calculate_similarity(
                        product1["features"], product2["features"]
                    )

                    if similarity >= self.title_similarity_threshold:
                        similar_products.append(product2)
                        processed_indices.add(j)

                # Create product match if we have multiple similar products
                if len(similar_products) > 1:
                    # Calculate average confidence score
                    avg_confidence = sum(
                        self.calculate_similarity(
                            similar_products[0]["features"], p["features"]
                        )
                        for p in similar_products
                    ) / len(similar_products)

                    # Create sites list
                    sites = []
                    for product in similar_products:
                        item = product["item"]
                        sites.append(
                            {
                                "source": item.get("source", "Unknown"),
                                "price": item.get("price", "Unknown"),
                                "url": item.get("url", ""),
                                "rating": item.get("rating", 0),
                                "reviews": item.get("reviews", 0),
                                "timestamp": item.get("timestamp", ""),
                                "features": product["features"],
                            }
                        )

                    # Create product match
                    first_item = similar_products[0]["item"]
                    product_match = ProductMatch(
                        product_id=f"match_{len(matched_groups)}",
                        title=first_item.get("title", "Unknown"),
                        category=first_item.get("category", "Unknown"),
                        brand=similar_products[0]["features"].get("brand"),
                        model=similar_products[0]["features"].get("model"),
                        confidence_score=avg_confidence,
                        sites=sites,
                    )

                    matched_groups.append(product_match)

            self.logger.info(f"Created {len(matched_groups)} product matches")
            return matched_groups

        except Exception as e:
            self.logger.error(f"Error matching products: {e}")
            return []

    def analyze_price_comparison(self, product_match: ProductMatch) -> PriceComparison:
        """
        Analyze price comparison for a matched product.

        Args:
            product_match: Matched product group

        Returns:
            Price comparison analysis
        """
        try:
            if not product_match.sites:
                return None

            # Extract and clean prices
            prices = []
            price_distribution = {}

            for site in product_match.sites:
                price_str = site.get("price", "0")
                try:
                    # Extract numeric price
                    price_numeric = float(re.sub(r"[^\d.]", "", price_str))
                    prices.append(price_numeric)

                    # Track price by source
                    source = site.get("source", "Unknown")
                    if source not in price_distribution:
                        price_distribution[source] = price_numeric
                    else:
                        # If multiple prices from same source, take average
                        price_distribution[source] = (
                            price_distribution[source] + price_numeric
                        ) / 2

                except (ValueError, TypeError):
                    continue

            if not prices:
                return None

            # Calculate price statistics
            prices_array = np.array(prices)
            best_price = float(np.min(prices_array))
            worst_price = float(np.max(prices_array))
            average_price = float(np.mean(prices_array))
            price_range = worst_price - best_price
            price_variance = float(np.var(prices_array))

            # Generate recommendations
            recommendations = []

            if price_range > average_price * 0.3:
                recommendations.append(
                    "High price variability - shop around for best deals"
                )

            if price_variance > average_price * 0.1:
                recommendations.append("Significant price differences between sources")

            if len(prices) >= 3:
                recommendations.append(f"Compare prices across {len(prices)} sources")

            # Find best and worst sites
            best_site = min(price_distribution.items(), key=lambda x: x[1])[0]
            worst_site = max(price_distribution.items(), key=lambda x: x[1])[0]

            recommendations.append(f"Best price: {best_site} (${best_price:.2f})")
            recommendations.append(f"Worst price: {worst_site} (${worst_price:.2f})")

            return PriceComparison(
                product_id=product_match.product_id,
                title=product_match.title,
                category=product_match.category,
                best_price=best_price,
                worst_price=worst_price,
                average_price=average_price,
                price_range=price_range,
                price_variance=price_variance,
                site_count=len(prices),
                price_distribution=price_distribution,
                recommendations=recommendations,
                last_updated=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Error analyzing price comparison: {e}")
            return None

    def analyze_deals(
        self, product_match: ProductMatch, price_comparison: PriceComparison
    ) -> DealAnalysis:
        """
        Analyze deals and savings for a product.

        Args:
            product_match: Matched product group
            price_comparison: Price comparison analysis

        Returns:
            Deal analysis results
        """
        try:
            if not price_comparison:
                return None

            # Calculate deal metrics
            price_range = price_comparison.price_range
            average_price = price_comparison.average_price
            best_price = price_comparison.best_price

            # Calculate savings percentage
            if average_price > 0:
                savings_percentage = (price_range / average_price) * 100
            else:
                savings_percentage = 0.0

            # Calculate deal score (0-100)
            deal_score = min(savings_percentage * 4, 100)  # Scale savings to 0-100

            # Determine deal type
            if savings_percentage >= self.excellent_deal_threshold * 100:
                deal_type = "excellent"
            elif savings_percentage >= self.good_deal_threshold * 100:
                deal_type = "good"
            elif savings_percentage >= self.fair_deal_threshold * 100:
                deal_type = "fair"
            else:
                deal_type = "poor"

            # Generate recommendations
            recommendations = []

            if deal_type == "excellent":
                recommendations.append("Excellent deal! Significant savings available")
                recommendations.append("Consider buying from the lowest-priced source")
            elif deal_type == "good":
                recommendations.append("Good deal with noticeable savings")
                recommendations.append("Compare shipping and return policies")
            elif deal_type == "fair":
                recommendations.append("Fair pricing with moderate savings")
                recommendations.append("Check for additional discounts or coupons")
            else:
                recommendations.append("Limited price variation between sources")
                recommendations.append("Focus on service quality and shipping speed")

            # Add price-specific recommendations
            if price_comparison.site_count >= 3:
                recommendations.append(
                    f"Compare across {price_comparison.site_count} sources"
                )

            if price_comparison.price_variance > average_price * 0.1:
                recommendations.append(
                    "High price variance - verify product authenticity"
                )

            # Get best and worst sites
            best_site = min(
                price_comparison.price_distribution.items(), key=lambda x: x[1]
            )[0]
            worst_site = max(
                price_comparison.price_distribution.items(), key=lambda x: x[1]
            )[0]

            # Create price history (simplified)
            price_history = []
            for site in product_match.sites:
                price_history.append(
                    {
                        "source": site.get("source"),
                        "price": site.get("price"),
                        "timestamp": site.get("timestamp"),
                        "rating": site.get("rating", 0),
                    }
                )

            return DealAnalysis(
                product_id=product_match.product_id,
                title=product_match.title,
                deal_score=deal_score,
                deal_type=deal_type,
                savings_percentage=savings_percentage,
                price_difference=price_range,
                best_site=best_site,
                worst_site=worst_site,
                price_history=price_history,
                recommendations=recommendations,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing deals: {e}")
            return None

    def generate_comparison_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive comparison report.

        Args:
            data: List of scraped data items

        Returns:
            Dictionary with comparison analysis results
        """
        try:
            if not data:
                return {"error": "No data available for comparison"}

            # Match products
            product_matches = self.match_products(data)

            if not product_matches:
                return {"error": "No product matches found"}

            # Analyze each product match
            price_comparisons = []
            deal_analyses = []

            for product_match in product_matches:
                # Price comparison analysis
                price_comparison = self.analyze_price_comparison(product_match)
                if price_comparison:
                    price_comparisons.append(price_comparison)

                # Deal analysis
                deal_analysis = self.analyze_deals(product_match, price_comparison)
                if deal_analysis:
                    deal_analyses.append(deal_analysis)

            # Generate summary statistics
            if price_comparisons:
                avg_price_range = np.mean([pc.price_range for pc in price_comparisons])
                avg_savings = np.mean([da.savings_percentage for da in deal_analyses])
                excellent_deals = len(
                    [da for da in deal_analyses if da.deal_type == "excellent"]
                )
                good_deals = len([da for da in deal_analyses if da.deal_type == "good"])
            else:
                avg_price_range = 0.0
                avg_savings = 0.0
                excellent_deals = 0
                good_deals = 0

            # Create report
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_products": len(product_matches),
                    "total_comparisons": len(price_comparisons),
                    "total_deals": len(deal_analyses),
                    "average_price_range": float(avg_price_range),
                    "average_savings_percentage": float(avg_savings),
                    "excellent_deals": excellent_deals,
                    "good_deals": good_deals,
                },
                "product_matches": [
                    {
                        "product_id": pm.product_id,
                        "title": pm.title,
                        "category": pm.category,
                        "brand": pm.brand,
                        "model": pm.model,
                        "confidence_score": pm.confidence_score,
                        "site_count": len(pm.sites),
                    }
                    for pm in product_matches
                ],
                "price_comparisons": [
                    {
                        "product_id": pc.product_id,
                        "title": pc.title,
                        "best_price": pc.best_price,
                        "worst_price": pc.worst_price,
                        "average_price": pc.average_price,
                        "price_range": pc.price_range,
                        "site_count": pc.site_count,
                        "recommendations": pc.recommendations,
                    }
                    for pc in price_comparisons
                ],
                "deal_analyses": [
                    {
                        "product_id": da.product_id,
                        "title": da.title,
                        "deal_score": da.deal_score,
                        "deal_type": da.deal_type,
                        "savings_percentage": da.savings_percentage,
                        "best_site": da.best_site,
                        "worst_site": da.worst_site,
                        "recommendations": da.recommendations,
                    }
                    for da in deal_analyses
                ],
                "recommendations": self._generate_overall_recommendations(
                    price_comparisons, deal_analyses
                ),
            }

            # Save report
            self._save_comparison_report(report)

            self.logger.info("Comparison report generated successfully")
            return report

        except Exception as e:
            self.logger.error(f"Error generating comparison report: {e}")
            return {"error": str(e)}

    def _generate_overall_recommendations(
        self,
        price_comparisons: List[PriceComparison],
        deal_analyses: List[DealAnalysis],
    ) -> List[str]:
        """Generate overall recommendations based on analysis."""
        try:
            recommendations = []

            if not price_comparisons:
                return ["No price comparisons available"]

            # Analyze deal distribution
            deal_types = [da.deal_type for da in deal_analyses]
            excellent_count = deal_types.count("excellent")
            good_count = deal_types.count("good")

            if excellent_count > 0:
                recommendations.append(
                    f"Found {excellent_count} excellent deals - great time to buy!"
                )

            if good_count > 0:
                recommendations.append(
                    f"Found {good_count} good deals with noticeable savings"
                )

            # Analyze price ranges
            avg_price_range = np.mean([pc.price_range for pc in price_comparisons])
            if avg_price_range > 50:
                recommendations.append(
                    "High price variability detected - significant savings opportunities"
                )

            # Analyze site coverage
            avg_site_count = np.mean([pc.site_count for pc in price_comparisons])
            if avg_site_count < 2:
                recommendations.append(
                    "Limited site coverage - consider expanding data sources"
                )
            elif avg_site_count >= 3:
                recommendations.append(
                    f"Good site coverage ({avg_site_count:.1f} sites average)"
                )

            # Analyze categories
            categories = [pc.category for pc in price_comparisons]
            category_counts = pd.Series(categories).value_counts()
            if len(category_counts) > 0:
                top_category = category_counts.index[0]
                recommendations.append(f"Most compared category: {top_category}")

            if not recommendations:
                recommendations.append("Continue monitoring prices for better deals")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating overall recommendations: {e}")
            return ["Error generating recommendations"]

    def _save_comparison_report(self, report: Dict[str, Any]):
        """Save comparison report to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.json"
            filepath = self.data_directory / "comparisons" / filename

            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Comparison report saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving comparison report: {e}")

    def find_best_deals(
        self, data: List[Dict[str, Any]], min_deal_score: float = 70.0
    ) -> List[DealAnalysis]:
        """
        Find the best deals in the data.

        Args:
            data: List of scraped data items
            min_deal_score: Minimum deal score to consider

        Returns:
            List of best deals
        """
        try:
            if not data:
                return []

            # Generate comparison report
            report = self.generate_comparison_report(data)

            if "error" in report:
                return []

            # Extract deal analyses
            product_matches = self.match_products(data)
            best_deals = []

            for product_match in product_matches:
                price_comparison = self.analyze_price_comparison(product_match)
                if price_comparison:
                    deal_analysis = self.analyze_deals(product_match, price_comparison)
                    if deal_analysis and deal_analysis.deal_score >= min_deal_score:
                        best_deals.append(deal_analysis)

            # Sort by deal score (descending)
            best_deals.sort(key=lambda x: x.deal_score, reverse=True)

            self.logger.info(f"Found {len(best_deals)} best deals")
            return best_deals

        except Exception as e:
            self.logger.error(f"Error finding best deals: {e}")
            return []

    def compare_specific_product(
        self, product_title: str, data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Compare prices for a specific product.

        Args:
            product_title: Title of the product to compare
            data: List of scraped data items

        Returns:
            Comparison results for the specific product
        """
        try:
            if not data:
                return None

            # Find products similar to the specified title
            target_features = self.extract_product_features(product_title)

            similar_products = []
            for item in data:
                item_features = self.extract_product_features(
                    item.get("title", ""), item.get("category")
                )

                similarity = self.calculate_similarity(target_features, item_features)
                if similarity >= self.title_similarity_threshold:
                    similar_products.append(item)

            if not similar_products:
                return {"error": f"No similar products found for '{product_title}'"}

            # Create a product match for the similar products
            sites = []
            for item in similar_products:
                sites.append(
                    {
                        "source": item.get("source", "Unknown"),
                        "price": item.get("price", "Unknown"),
                        "url": item.get("url", ""),
                        "rating": item.get("rating", 0),
                        "reviews": item.get("reviews", 0),
                        "timestamp": item.get("timestamp", ""),
                    }
                )

            product_match = ProductMatch(
                product_id="specific_product",
                title=product_title,
                category=similar_products[0].get("category", "Unknown"),
                sites=sites,
            )

            # Analyze the product
            price_comparison = self.analyze_price_comparison(product_match)
            deal_analysis = self.analyze_deals(product_match, price_comparison)

            return {
                "product_title": product_title,
                "similar_products_found": len(similar_products),
                "price_comparison": price_comparison.__dict__
                if price_comparison
                else None,
                "deal_analysis": deal_analysis.__dict__ if deal_analysis else None,
            }

        except Exception as e:
            self.logger.error(f"Error comparing specific product: {e}")
            return {"error": str(e)}
