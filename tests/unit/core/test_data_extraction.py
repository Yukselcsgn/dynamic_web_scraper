from unittest.mock import MagicMock

import pytest

from scraper.core.data_extraction import DataExtractor


@pytest.fixture
def mock_universal_extractor():
    return MagicMock()


@pytest.fixture
def data_extractor(mock_universal_extractor):
    return DataExtractor(mock_universal_extractor)


@pytest.fixture
def sample_html_product_list():
    return """
    <html>
        <body>
            <div class="product">
                <h2 class="title"><a href="/p/1">Product 1</a></h2>
                <span class="price">$10.00</span>
                <p class="description">Description 1</p>
                <img src="/img/1.jpg" />
            </div>
            <div class="product">
                <h2 class="title">Product 2</h2>
                <span class="price">$20.00</span>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_json_ld():
    return """
    <html>
        <body>
            <script type="application/ld+json">
            [
                {"@type": "Product", "name": "JSON Product", "offers": {"price": "30.00"}}
            ]
            </script>
        </body>
    </html>
    """


class TestDataExtractor:
    def test_extract_with_smart_selectors(self, data_extractor):
        """Test extraction using site profile smart selectors."""
        # Arrange
        html = """
        <div class="custom-card">
            <h3 class="custom-title">Custom Item</h3>
            <div class="custom-price">99.99 TL</div>
        </div>
        """
        site_profile = MagicMock()
        site_profile.selectors = {
            "product_container": ".custom-card",
            "title": ".custom-title",
            "price": ".custom-price",
        }

        # Act
        results = data_extractor.extract_data(html, site_profile)

        # Assert
        assert len(results) == 1
        assert results[0]["title"] == "Custom Item"
        assert results[0]["price"] == "99.99 TL"

    def test_extract_with_default_selectors_success(
        self, data_extractor, sample_html_product_list
    ):
        """Test extraction using default common selectors."""
        # Act
        results = data_extractor.extract_data(sample_html_product_list)

        # Assert
        assert len(results) == 2

        # Item 1 Check
        assert results[0]["title"] == "Product 1"
        assert results[0]["price"] == "$10.00"
        assert results[0]["description"] == "Description 1"
        assert results[0]["url"] == "/p/1"
        assert results[0]["image_url"] == "/img/1.jpg"

        # Item 2 Check (Partial data)
        assert results[1]["title"] == "Product 2"
        assert results[1]["price"] == "$20.00"
        assert "url" not in results[1]

    def test_extract_structured_data_fallback(
        self, data_extractor, sample_html_json_ld
    ):
        """Test fallback to JSON-LD structured data when no selectors match."""
        # Act
        results = data_extractor.extract_data(sample_html_json_ld)

        # Assert
        assert len(results) == 1
        assert results[0]["name"] == "JSON Product"
        assert results[0]["offers"]["price"] == "30.00"

    def test_clean_text(self, data_extractor):
        """Test text cleaning utility."""
        dirty_text = "  Dirty   Text\n\t with  symbols!!! "
        cleaned = data_extractor._clean_text(dirty_text)
        assert cleaned == "Dirty Text with symbols!!!"

        # Test empty
        assert data_extractor._clean_text(None) == ""
        assert data_extractor._clean_text("") == ""

    def test_extract_sahibinden_data_direct_call(self, data_extractor):
        """Test specific sahibinden extraction method."""
        html = """
        <div class="classified-item">
            <div class="classified-title"><a href="/ad/1">Car For Sale</a></div>
            <div class="classified-price">500,000 TL</div>
            <div class="classified-location">Istanbul</div>
        </div>
        """
        # Act
        results = data_extractor._extract_sahibinden_data(html)

        # Assert
        assert len(results) == 1
        assert results[0]["title"] == "Car For Sale"
        assert results[0]["price"] == "500,000 TL"
        assert results[0]["location"] == "Istanbul"

    def test_malformed_html_handling(self, data_extractor):
        """Test graceful handling of malformed HTML."""
        html = "<div><span class='product'>Unclosed Tag"
        # Should rely on BeautifulSoup's robust parsing
        results = data_extractor.extract_data(html)
        # Even if minimal, it shouldn't crash
        assert isinstance(results, list)

    def test_empty_html_handling(self, data_extractor):
        """Test handling of empty HTML input."""
        results = data_extractor.extract_data("")
        assert results == []
