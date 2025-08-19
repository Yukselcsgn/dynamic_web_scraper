"""
CSS rule management utilities for the dynamic web scraper project.
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CSSRule:
    """Represents a CSS rule for web scraping."""

    name: str
    selector: str
    attribute: Optional[str] = None
    transform: Optional[str] = None
    required: bool = True
    fallback: Optional[str] = None
    description: str = ""


class CSSRuleManager:
    """Manages CSS rules for different websites and selectors."""

    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize the CSS rule manager.

        Args:
            rules_file: Path to JSON file containing CSS rules
        """
        self.rules: Dict[str, List[CSSRule]] = {}
        self.rules_file = rules_file

        if rules_file and Path(rules_file).exists():
            self.load_rules(rules_file)

    def add_rule(self, site_name: str, rule: CSSRule) -> None:
        """
        Add a CSS rule for a specific site.

        Args:
            site_name: Name of the website
            rule: CSSRule object to add
        """
        if site_name not in self.rules:
            self.rules[site_name] = []

        # Check for duplicate rules
        existing_rule = next(
            (r for r in self.rules[site_name] if r.name == rule.name), None
        )
        if existing_rule:
            # Update existing rule
            index = self.rules[site_name].index(existing_rule)
            self.rules[site_name][index] = rule
        else:
            self.rules[site_name].append(rule)

    def get_rules(self, site_name: str) -> List[CSSRule]:
        """
        Get all CSS rules for a specific site.

        Args:
            site_name: Name of the website

        Returns:
            List of CSSRule objects
        """
        return self.rules.get(site_name, [])

    def get_rule(self, site_name: str, rule_name: str) -> Optional[CSSRule]:
        """
        Get a specific CSS rule by name.

        Args:
            site_name: Name of the website
            rule_name: Name of the rule

        Returns:
            CSSRule object or None if not found
        """
        rules = self.get_rules(site_name)
        return next((rule for rule in rules if rule.name == rule_name), None)

    def remove_rule(self, site_name: str, rule_name: str) -> bool:
        """
        Remove a CSS rule by name.

        Args:
            site_name: Name of the website
            rule_name: Name of the rule to remove

        Returns:
            True if rule was removed, False if not found
        """
        if site_name not in self.rules:
            return False

        rules = self.rules[site_name]
        for i, rule in enumerate(rules):
            if rule.name == rule_name:
                del rules[i]
                return True

        return False

    def validate_rule(self, rule: CSSRule) -> List[str]:
        """
        Validate a CSS rule and return any issues.

        Args:
            rule: CSSRule object to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check required fields
        if not rule.name:
            errors.append("Rule name is required")

        if not rule.selector:
            errors.append("CSS selector is required")

        # Validate selector syntax (basic check)
        if rule.selector:
            # Check for basic CSS selector patterns
            if not re.match(
                r"^[.#]?[a-zA-Z][a-zA-Z0-9_-]*(\.[a-zA-Z][a-zA-Z0-9_-]*)*(\[[^\]]*\])*(\:[a-zA-Z-]+(\([^)]*\))?)*$",
                rule.selector,
            ):
                errors.append("Invalid CSS selector syntax")

        # Validate transform if provided
        if rule.transform and rule.transform not in [
            "text",
            "href",
            "src",
            "title",
            "alt",
        ]:
            errors.append("Invalid transform value")

        return errors

    def save_rules(self, file_path: Optional[str] = None) -> None:
        """
        Save CSS rules to a JSON file.

        Args:
            file_path: Path to save the rules (uses self.rules_file if not provided)
        """
        file_path = file_path or self.rules_file
        if not file_path:
            raise ValueError("No file path provided for saving rules")

        # Convert rules to dictionary format
        rules_dict = {}
        for site_name, rules in self.rules.items():
            rules_dict[site_name] = [asdict(rule) for rule in rules]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rules_dict, f, indent=2, ensure_ascii=False)

    def load_rules(self, file_path: str) -> None:
        """
        Load CSS rules from a JSON file.

        Args:
            file_path: Path to the JSON file containing rules
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Rules file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            rules_dict = json.load(f)

        # Convert dictionary back to CSSRule objects
        for site_name, rules_list in rules_dict.items():
            self.rules[site_name] = []
            for rule_dict in rules_list:
                rule = CSSRule(**rule_dict)
                self.rules[site_name].append(rule)

    def get_site_names(self) -> List[str]:
        """
        Get list of all site names that have rules.

        Returns:
            List of site names
        """
        return list(self.rules.keys())

    def export_rules_for_site(self, site_name: str) -> Dict[str, Any]:
        """
        Export rules for a specific site in a format suitable for scraping.

        Args:
            site_name: Name of the website

        Returns:
            Dictionary with rule names as keys and selectors as values
        """
        rules = self.get_rules(site_name)
        export_dict = {}

        for rule in rules:
            export_dict[rule.name] = {
                "selector": rule.selector,
                "attribute": rule.attribute,
                "transform": rule.transform,
                "required": rule.required,
                "fallback": rule.fallback,
            }

        return export_dict

    def create_default_rules(self, site_name: str) -> None:
        """
        Create default CSS rules for common e-commerce elements.

        Args:
            site_name: Name of the website
        """
        default_rules = [
            CSSRule(
                name="product_container",
                selector=".product, .item, .card, .listing",
                description="Container element for individual products",
            ),
            CSSRule(
                name="product_title",
                selector=".product-title, .item-title, .card-title, h1, h2, h3",
                attribute="text",
                transform="text",
                description="Product title or name",
            ),
            CSSRule(
                name="product_price",
                selector=".price, .cost, .amount, [class*='price']",
                attribute="text",
                transform="text",
                description="Product price",
            ),
            CSSRule(
                name="product_image",
                selector="img",
                attribute="src",
                transform="src",
                description="Product image URL",
            ),
            CSSRule(
                name="product_link",
                selector="a",
                attribute="href",
                transform="href",
                description="Product detail page link",
            ),
            CSSRule(
                name="product_description",
                selector=".description, .desc, .summary",
                attribute="text",
                transform="text",
                required=False,
                description="Product description",
            ),
        ]

        for rule in default_rules:
            self.add_rule(site_name, rule)
