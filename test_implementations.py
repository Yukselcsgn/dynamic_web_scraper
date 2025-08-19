#!/usr/bin/env python3
"""
Simple test script to verify our implementations work correctly.
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_css_selector_generator():
    """Test CSS selector generator functionality."""
    print("Testing CSS Selector Generator...")
    try:
        from scraper.css_selectors.css_selector_generator import (
            generate_selector,
            find_product_selectors,
            validate_selector,
        )
        from bs4 import BeautifulSoup

        # Test HTML
        html = """
        <div class="product-item" data-product-id="123">
            <h2 class="product-title">Test Product</h2>
            <span class="product-price">$99.99</span>
        </div>
        """

        # Test selector generation
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find(class_="product-title")
        selector = generate_selector(element)
        print(f"✓ Generated selector: {selector}")

        # Test product selector finding
        selectors = find_product_selectors(html)
        print(f"✓ Found {len(selectors['product_titles'])} product title selectors")

        # Test selector validation
        is_valid = validate_selector(html, ".product-title")
        print(f"✓ Selector validation: {is_valid}")

        return True
    except Exception as e:
        print(f"✗ CSS Selector Generator failed: {e}")
        return False


def test_css_rules():
    """Test CSS rules functionality."""
    print("\nTesting CSS Rules...")
    try:
        from scraper.css_selectors.css_rules import CSSRuleManager, CSSRule

        # Create rule manager
        rule_manager = CSSRuleManager()

        # Create a test rule
        rule = CSSRule(
            name="product_title",
            selector=".product-title",
            attribute="text",
            transform="text",
            description="Product title selector",
        )

        # Add rule
        rule_manager.add_rule("test_site", rule)
        rules = rule_manager.get_rules("test_site")
        print(f"✓ Added rule: {len(rules)} rules found")

        # Test rule retrieval
        retrieved_rule = rule_manager.get_rule("test_site", "product_title")
        print(f"✓ Retrieved rule: {retrieved_rule.name}")

        # Test default rules
        rule_manager.create_default_rules("default_site")
        default_rules = rule_manager.get_rules("default_site")
        print(f"✓ Created {len(default_rules)} default rules")

        return True
    except Exception as e:
        print(f"✗ CSS Rules failed: {e}")
        return False


def test_dynamic_selector():
    """Test dynamic selector functionality."""
    print("\nTesting Dynamic Selector...")
    try:
        from scraper.css_selectors.dynamic_selector import DynamicSelector

        # Create dynamic selector
        dynamic_selector = DynamicSelector()

        # Test HTML
        html = """
        <div class="product-container">
            <h2 class="product-title">Test Product</h2>
            <span class="product-price">$99.99</span>
        </div>
        """

        # Test site type detection
        url = "https://www.amazon.com/products"
        site_type = dynamic_selector.detect_site_type(url, html)
        print(f"✓ Detected site type: {site_type}")

        # Test selector generation
        selectors = dynamic_selector.generate_selectors(html, "ecommerce")
        print(f"✓ Generated {len(selectors['product_containers'])} container selectors")

        # Test site adaptation
        result = dynamic_selector.adapt_to_site(url, html)
        print(f"✓ Site adaptation confidence: {result['confidence']:.2f}")

        return True
    except Exception as e:
        print(f"✗ Dynamic Selector failed: {e}")
        return False


def test_html_analyzer():
    """Test HTML analyzer functionality."""
    print("\nTesting HTML Analyzer...")
    try:
        from scraper.site_detection.html_analyzer import (
            analyze_html,
            detect_ecommerce_patterns,
        )

        # Test HTML
        html = """
        <html>
            <head>
                <title>Test Shop</title>
                <meta name="description" content="Online shopping">
            </head>
            <body>
                <div class="product-grid">
                    <div class="product-item">
                        <h2>Product Title</h2>
                        <span class="price">$99.99</span>
                        <button>Add to Cart</button>
                    </div>
                </div>
            </body>
        </html>
        """

        # Test HTML analysis
        analysis = analyze_html(html, "https://testshop.com")
        print(f"✓ Analyzed page title: {analysis['page_info']['title']}")
        print(f"✓ Found {len(analysis['content']['paragraphs'])} paragraphs")

        # Test e-commerce pattern detection
        patterns = detect_ecommerce_patterns(html)
        print(f"✓ E-commerce confidence: {patterns['confidence_score']}%")

        return True
    except Exception as e:
        print(f"✗ HTML Analyzer failed: {e}")
        return False


def test_css_selector_builder():
    """Test CSS selector builder functionality."""
    print("\nTesting CSS Selector Builder...")
    try:
        from scraper.site_detection.css_selector_builder import (
            build_selector,
            build_product_selectors,
            validate_selector_stability,
        )
        from bs4 import BeautifulSoup

        # Test HTML
        html = """
        <div class="product-item" data-product-id="123">
            <h2 class="product-title">Test Product</h2>
            <span class="product-price">$99.99</span>
        </div>
        """

        soup = BeautifulSoup(html, "html.parser")
        element = soup.find(class_="product-title")

        # Test selector building
        selector = build_selector(element, "smart")
        print(f"✓ Built selector: {selector}")

        # Test product selector building
        selectors = build_product_selectors(html)
        print(f"✓ Built {len(selectors['titles'])} title selectors")

        # Test selector stability
        stability = validate_selector_stability(selector, html)
        print(f"✓ Selector stability: {stability:.2f}")

        return True
    except Exception as e:
        print(f"✗ CSS Selector Builder failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Dynamic Web Scraper Implementations\n")
    print("=" * 50)

    tests = [
        test_css_selector_generator,
        test_css_rules,
        test_dynamic_selector,
        test_html_analyzer,
        test_css_selector_builder,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Implementations are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementations.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
