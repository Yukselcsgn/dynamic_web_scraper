#!/usr/bin/env python3
"""
Quick verification script to test that DataProcessor initializes correctly.
This tests the fix for the AttributeError: 'DataProcessor' object has no attribute 'data_visualizer'
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.core.data_processing import DataProcessor


def test_dataprocessor_initialization():
    """Test that DataProcessor can be initialized without AttributeError."""

    print("Testing DataProcessor initialization...")

    # Create mock dependencies (None is acceptable for optional dependencies)
    mock_enricher = None
    mock_analyzer = None
    mock_visualizer = None  # This was causing the bug when accessed before assignment
    mock_reporter = None
    mock_comparator = None
    mock_plugin_mgr = None

    try:
        # Initialize DataProcessor
        processor = DataProcessor(
            data_enricher=mock_enricher,
            price_analyzer=mock_analyzer,
            data_visualizer=mock_visualizer,
            automated_reporter=mock_reporter,
            site_comparator=mock_comparator,
            plugin_manager=mock_plugin_mgr,
        )

        print("✅ SUCCESS: DataProcessor initialized without errors")
        print(f"   - data_enricher: {processor.data_enricher}")
        print(f"   - price_analyzer: {processor.price_analyzer}")
        print(f"   - data_visualizer: {processor.data_visualizer}")
        print(f"   - automated_reporter: {processor.automated_reporter}")
        print(f"   - site_comparator: {processor.site_comparator}")
        print(f"   - plugin_manager: {processor.plugin_manager}")

        # Verify the attribute exists
        assert hasattr(
            processor, "data_visualizer"
        ), "Missing data_visualizer attribute"
        print("\n✅ PASSED: All attributes properly assigned")

        return True

    except AttributeError as e:
        print(f"❌ FAILED: AttributeError occurred - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False


def test_create_visualizations():
    """Test that create_data_visualizations handles None visualizer gracefully."""

    print("\n" + "=" * 60)
    print("Testing create_data_visualizations with None visualizer...")

    processor = DataProcessor(
        data_enricher=None,
        price_analyzer=None,
        data_visualizer=None,  # No visualizer available
        automated_reporter=None,
        site_comparator=None,
        plugin_manager=None,
    )

    test_data = [
        {"name": "Product 1", "price": 10.99},
        {"name": "Product 2", "price": 15.99},
    ]

    try:
        result = processor.create_data_visualizations(test_data)
        print(f"✅ SUCCESS: Method returned {result}")
        print("   Expected: Empty list when visualizer is None")
        assert result == [], "Should return empty list when visualizer is None"
        print("✅ PASSED: Handles None visualizer correctly")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DataProcessor Fix Verification")
    print("=" * 60)

    test1_passed = test_dataprocessor_initialization()
    test2_passed = test_create_visualizations()

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Initialization Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Visualization Test:  {'✅ PASSED' if test2_passed else '❌ FAILED'}")

    if test1_passed and test2_passed:
        print("\n🎉 All tests PASSED! The bug is fixed.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED. Please review the errors.")
        sys.exit(1)
