"""
Tests for CSS selector functionality.
"""

from bs4 import BeautifulSoup
from scraper.css_selectors.css_selector_generator import (
    generate_selector,
    generate_unique_selector,
    find_product_selectors,
    validate_selector,
    optimize_selector,
)
from scraper.css_selectors.css_rules import CSSRuleManager, CSSRule
from scraper.css_selectors.dynamic_selector import DynamicSelector


class TestCSSSelectorGenerator:
    """Test CSS selector generator functionality."""

    def setup_method(self):
        """Set up test data."""
        self.sample_html = """
        <html>
            <body>
                <div id="main-container" class="product-listing">
                    <div class="product-item" data-product-id="123">
                        <h2 class="product-title">Test Product</h2>
                        <span class="product-price">$99.99</span>
                        <img src="test.jpg" alt="Product Image" class="product-image">
                        <a href="/product/123" class="product-link">View Details</a>
                    </div>
                    <div class="product-item" data-product-id="456">
                        <h2 class="product-title">Another Product</h2>
                        <span class="product-price">$149.99</span>
                        <img src="test2.jpg" alt="Product Image" class="product-image">
                        <a href="/product/456" class="product-link">View Details</a>
                    </div>
                </div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.sample_html, "html.parser")

    def test_generate_selector_with_id(self):
        """Test generating selector for element with ID."""
        element = self.soup.find(id="main-container")
        selector = generate_selector(element)
        assert selector == "#main-container"

    def test_generate_selector_with_class(self):
        """Test generating selector for element with class."""
        element = self.soup.find(class_="product-title")
        selector = generate_selector(element)
        assert "product-title" in selector

    def test_generate_selector_with_data_attribute(self):
        """Test generating selector for element with data attribute."""
        element = self.soup.find(attrs={"data-product-id": "123"})
        selector = generate_selector(element)
        assert "data-product-id" in selector

    def test_generate_unique_selector(self):
        """Test generating unique selector."""
        element = self.soup.find(class_="product-title")
        selector = generate_unique_selector(element)
        assert "product-title" in selector
        assert len(selector.split(" > ")) > 1

    def test_find_product_selectors(self):
        """Test finding product selectors."""
        selectors = find_product_selectors(self.sample_html)

        assert "product_containers" in selectors
        assert "product_titles" in selectors
        assert "product_prices" in selectors
        assert "product_images" in selectors
        assert "product_links" in selectors

        # Should find some selectors
        assert len(selectors["product_containers"]) > 0
        assert len(selectors["product_titles"]) > 0

    def test_validate_selector(self):
        """Test selector validation."""
        # Valid selector
        assert validate_selector(self.sample_html, ".product-title") is True

        # Invalid selector
        assert validate_selector(self.sample_html, ".non-existent-class") is False

    def test_optimize_selector(self):
        """Test selector optimization."""
        selector = optimize_selector(self.sample_html, ".product-title")
        assert selector == ".product-title"


class TestCSSRuleManager:
    """Test CSS rule manager functionality."""

    def setup_method(self):
        """Set up test data."""
        self.rule_manager = CSSRuleManager()
        self.sample_rule = CSSRule(
            name="product_title",
            selector=".product-title",
            attribute="text",
            transform="text",
            description="Product title selector",
        )

    def test_add_rule(self):
        """Test adding a CSS rule."""
        self.rule_manager.add_rule("test_site", self.sample_rule)
        rules = self.rule_manager.get_rules("test_site")
        assert len(rules) == 1
        assert rules[0].name == "product_title"

    def test_get_rule(self):
        """Test getting a specific rule."""
        self.rule_manager.add_rule("test_site", self.sample_rule)
        rule = self.rule_manager.get_rule("test_site", "product_title")
        assert rule is not None
        assert rule.selector == ".product-title"

    def test_remove_rule(self):
        """Test removing a rule."""
        self.rule_manager.add_rule("test_site", self.sample_rule)
        assert self.rule_manager.remove_rule("test_site", "product_title") is True
        assert len(self.rule_manager.get_rules("test_site")) == 0

    def test_validate_rule(self):
        """Test rule validation."""
        # Valid rule
        errors = self.rule_manager.validate_rule(self.sample_rule)
        assert len(errors) == 0

        # Invalid rule (missing name)
        invalid_rule = CSSRule(name="", selector=".test")
        errors = self.rule_manager.validate_rule(invalid_rule)
        assert len(errors) > 0

    def test_create_default_rules(self):
        """Test creating default rules."""
        self.rule_manager.create_default_rules("test_site")
        rules = self.rule_manager.get_rules("test_site")
        assert len(rules) > 0

        # Check for common rule names
        rule_names = [rule.name for rule in rules]
        assert "product_container" in rule_names
        assert "product_title" in rule_names
        assert "product_price" in rule_names

    def test_export_rules_for_site(self):
        """Test exporting rules for a site."""
        self.rule_manager.add_rule("test_site", self.sample_rule)
        exported = self.rule_manager.export_rules_for_site("test_site")
        assert "product_title" in exported
        assert exported["product_title"]["selector"] == ".product-title"


class TestDynamicSelector:
    """Test dynamic selector functionality."""

    def setup_method(self):
        """Set up test data."""
        self.dynamic_selector = DynamicSelector()
        self.sample_html = """
        <html>
            <body>
                <div class="product-container">
                    <h2 class="product-title">Test Product</h2>
                    <span class="product-price">$99.99</span>
                    <img src="test.jpg" class="product-image">
                    <a href="/product/123" class="product-link">View Details</a>
                </div>
            </body>
        </html>
        """

    def test_detect_site_type_ecommerce(self):
        """Test detecting e-commerce site type."""
        url = "https://www.amazon.com/products"
        site_type = self.dynamic_selector.detect_site_type(url, self.sample_html)
        assert site_type == "ecommerce"

    def test_detect_site_type_unknown(self):
        """Test detecting unknown site type."""
        url = "https://www.example.com"
        site_type = self.dynamic_selector.detect_site_type(url, self.sample_html)
        assert site_type == "unknown"

    def test_generate_selectors(self):
        """Test generating selectors."""
        selectors = self.dynamic_selector.generate_selectors(
            self.sample_html, "ecommerce"
        )

        assert "product_containers" in selectors
        assert "product_titles" in selectors
        assert "product_prices" in selectors
        assert "product_images" in selectors
        assert "product_links" in selectors

    def test_find_best_selectors(self):
        """Test finding best selectors."""
        target_elements = ["product_containers", "product_titles", "product_prices"]
        best_selectors = self.dynamic_selector.find_best_selectors(
            self.sample_html, target_elements
        )

        assert len(best_selectors) > 0
        for element_type in target_elements:
            if element_type in best_selectors:
                assert best_selectors[element_type] != ""

    def test_adapt_to_site(self):
        """Test adapting to a specific site."""
        url = "https://www.testshop.com"
        result = self.dynamic_selector.adapt_to_site(url, self.sample_html)

        assert "site_type" in result
        assert "domain" in result
        assert "selectors" in result
        assert "best_selectors" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    def test_get_cached_selectors(self):
        """Test getting cached selectors."""
        url = "https://www.testshop.com"

        # Initially no cached data
        assert self.dynamic_selector.get_cached_selectors(url) is None

        # After adapting to site, should have cached data
        self.dynamic_selector.adapt_to_site(url, self.sample_html)
        cached = self.dynamic_selector.get_cached_selectors(url)
        assert cached is not None
        assert "site_type" in cached

    def test_clear_cache(self):
        """Test clearing the cache."""
        url = "https://www.testshop.com"
        self.dynamic_selector.adapt_to_site(url, self.sample_html)

        # Should have cached data
        assert self.dynamic_selector.get_cached_selectors(url) is not None

        # Clear cache
        self.dynamic_selector.clear_cache()
        assert self.dynamic_selector.get_cached_selectors(url) is None


class TestIntegration:
    """Integration tests for CSS selector functionality."""

    def test_full_selector_workflow(self):
        """Test the complete selector workflow."""
        # Sample e-commerce HTML
        html = """
        <html>
            <body>
                <div class="product-grid">
                    <div class="product-card" data-product-id="123">
                        <h3 class="product-name">iPhone 13</h3>
                        <div class="price-container">
                            <span class="price">$999</span>
                        </div>
                        <img src="iphone.jpg" class="product-image">
                        <a href="/product/123" class="buy-button">Buy Now</a>
                    </div>
                </div>
            </body>
        </html>
        """

        # Test dynamic selector
        dynamic_selector = DynamicSelector()
        result = dynamic_selector.adapt_to_site("https://testshop.com", html)

        assert result["site_type"] == "ecommerce"
        assert result["confidence"] > 0

        # Test CSS rule manager
        rule_manager = CSSRuleManager()
        rule_manager.create_default_rules("testshop.com")

        # Test selector generator
        selectors = find_product_selectors(html)
        assert len(selectors["product_containers"]) > 0

        # Test selector validation
        for element_type, selector_list in selectors.items():
            for selector in selector_list[:3]:  # Test first 3 selectors
                assert validate_selector(html, selector) is True
