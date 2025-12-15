from unittest.mock import MagicMock

import pytest

from scraper.core.data_processing import DataProcessor


@pytest.fixture
def mock_dependencies():
    return {
        "data_enricher": MagicMock(),
        "price_analyzer": MagicMock(),
        "data_visualizer": MagicMock(),
        "automated_reporter": MagicMock(),
        "site_comparator": MagicMock(),
        "plugin_manager": MagicMock(),
    }


@pytest.fixture
def data_processor(mock_dependencies):
    return DataProcessor(**mock_dependencies)


class TestDataProcessor:
    def test_enrich_data_success(self, data_processor, mock_dependencies):
        """Test successful data enrichment."""
        # Arrange
        raw_data = [{"id": 1}]
        mock_result = MagicMock()
        mock_result.quality_score = 0.95
        mock_dependencies["data_enricher"].enrich_data.return_value = mock_result

        # Act
        result = data_processor.enrich_data(raw_data)

        # Assert
        assert result == mock_result
        mock_dependencies["data_enricher"].enrich_data.assert_called_once_with(raw_data)

    def test_enrich_data_failure(self, data_processor, mock_dependencies):
        """Test enrichment failure handling."""
        # Arrange
        mock_dependencies["data_enricher"].enrich_data.side_effect = Exception(
            "Enrichment failed"
        )

        # Act
        result = data_processor.enrich_data([])

        # Assert
        assert result is None

    def test_analyze_prices_success(self, data_processor, mock_dependencies):
        """Test price analysis execution."""
        # Arrange
        data = [{"price": 100}]
        mock_analysis = MagicMock()
        mock_analysis.outliers = []
        mock_dependencies["price_analyzer"].analyze_prices.return_value = mock_analysis

        # Act
        result = data_processor.analyze_prices(data)

        # Assert
        assert result == mock_analysis
        mock_dependencies["price_analyzer"].analyze_prices.assert_called_once_with(data)

    def test_analyze_prices_disabled(self, data_processor):
        """Test price analysis when analyzer is None."""
        # Arrange
        data_processor.price_analyzer = None

        # Act
        result = data_processor.analyze_prices([])

        # Assert
        assert result is None

    def test_create_data_visualizations_success(
        self, data_processor, mock_dependencies
    ):
        """Test visualization creation."""
        # Arrange
        data = [{"a": 1}]
        mock_dependencies[
            "data_visualizer"
        ].create_comprehensive_dashboard.return_value = "dashboard.html"

        # Act
        result = data_processor.create_data_visualizations(data)

        # Assert
        assert result == ["dashboard.html"]
        mock_dependencies[
            "data_visualizer"
        ].create_comprehensive_dashboard.assert_called_once_with(data)

    def test_placeholder_methods(self, data_processor):
        """Test placeholder methods return expected empty structures."""
        data = []

        # Comparative Analysis
        comp = data_processor.perform_comparative_analysis(data)
        assert isinstance(comp, dict)
        assert "product_matches" in comp

        # Distributed Processing
        dist = data_processor.process_distributed(data)
        assert isinstance(dist, dict)
        assert "jobs_processed" in dist

        # Plugins
        plugins = data_processor.process_with_plugins(data)
        assert isinstance(plugins, dict)
        assert "active_plugins" in plugins

        # Reporting
        report = data_processor.generate_automated_report(data)
        assert isinstance(report, dict)
        assert "alerts" in report

    def test_get_processing_summary(self, data_processor):
        """Test processing summary generation."""
        # Arrange
        results = {
            "raw_data": [1, 2],
            "enriched_data": [1, 2],
            "processing_time": 1.5,
            "price_analysis": True,
            "comparison_analysis": False,
            "visualization_results": ["a"],
            "reporting_results": {},
        }

        # Act
        summary = data_processor.get_processing_summary(results)

        # Assert
        assert summary["raw_data_count"] == 2
        assert summary["processing_time"] == 1.5
        assert summary["price_analysis"] is True
        assert summary["visualizations_created"] == 1
