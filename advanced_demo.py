#!/usr/bin/env python3
"""
Advanced Demo Script - Showcases all the advanced features of the Dynamic Web Scraper.

This script demonstrates:
1. Smart Site Detection
2. Data Enrichment
3. Price Analysis
4. Advanced Analytics
5. Comprehensive Reporting
"""
import json
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.config import load_config
from scraper.core.scraper import Scraper
from scraper.data_processing.data_enricher import DataEnricher
from scraper.logging_manager.logging_manager import log_message, setup_logging


def print_banner():
    """Print a beautiful banner for the demo."""
    print("=" * 80)
    print("🚀 DYNAMIC WEB SCRAPER - ADVANCED FEATURES DEMO")
    print("=" * 80)
    print("✨ Smart Site Detection | 📊 Data Enrichment | 📈 Price Analysis")
    print("=" * 80)


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*20} {title} {'='*20}")


def demo_smart_detection():
    """Demonstrate smart site detection capabilities."""
    print_section("SMART SITE DETECTION")

    # Test URLs for different site types
    test_urls = [
        "https://www.sahibinden.com/alfa-romeo-giulietta",
        "https://httpbin.org/html",  # Simple test site
        "https://quotes.toscrape.com/",  # Quotes site
    ]

    config = load_config()

    for url in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        try:
            scraper = Scraper(url, config)
            profile = scraper.detect_site_profile()

            print(f"   📋 Site Type: {profile.site_type}")
            print(f"   🎯 Confidence: {profile.confidence:.2f}")
            print(f"   ⏱️  Wait Time: {profile.wait_time}s")
            print(f"   🤖 Use Selenium: {profile.use_selenium}")
            print(f"   🛡️  Anti-bot Measures: {profile.anti_bot_measures}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


def demo_data_enrichment():
    """Demonstrate data enrichment capabilities."""
    print_section("DATA ENRICHMENT")

    # Sample data for enrichment
    sample_data = [
        {
            "title": "iPhone 14 Pro Max 256GB",
            "price": "$1,199.00",
            "description": "Brand new iPhone 14 Pro Max. Contact: john@example.com or call +1-555-1234",
            "url": "https://example.com/iphone",
        },
        {
            "title": "MacBook Air M2 13-inch",
            "price": "€1,299.00",
            "description": "Excellent condition MacBook Air. Phone: +90-555-9876",
            "url": "https://example.com/macbook",
        },
        {
            "title": "Samsung Galaxy S23 Ultra",
            "price": "₺45,000",
            "description": "Like new Samsung phone. Email: seller@example.com",
            "url": "https://example.com/samsung",
        },
    ]

    enricher = DataEnricher()
    result = enricher.enrich_data(sample_data)

    print(f"📊 Enrichment Statistics:")
    print(f"   Original items: {result.enrichment_stats['original_count']}")
    print(f"   Enriched items: {result.enrichment_stats['enriched_count']}")
    print(
        f"   Processing time: {result.enrichment_stats['processing_time_seconds']:.2f}s"
    )
    print(f"   Quality score: {result.quality_score:.2f}")
    print(
        f"   Price extraction rate: {result.enrichment_stats['price_extraction_rate']:.1f}%"
    )
    print(
        f"   Category classification rate: {result.enrichment_stats['category_classification_rate']:.1f}%"
    )

    print(f"\n📋 Sample Enriched Data:")
    for i, item in enumerate(result.enriched_data[:2]):
        print(f"   Item {i+1}:")
        print(f"     Title: {item.get('title', 'N/A')}")
        print(
            f"     Normalized Price: {item.get('normalized_price', 'N/A')} {item.get('currency', 'N/A')}"
        )
        print(
            f"     Category: {item.get('category', 'N/A')} (confidence: {item.get('category_confidence', 0):.2f})"
        )
        print(f"     Quality Score: {item.get('quality_score', 0):.1f}/100")
        print(f"     Phone Numbers: {item.get('phone_numbers', [])}")
        print(f"     Email Addresses: {item.get('email_addresses', [])}")


def demo_price_analysis():
    """Demonstrate price analysis capabilities."""
    print_section("PRICE ANALYSIS")

    # Sample price data
    sample_data = [
        {"title": "Product A", "normalized_price": 100, "category": "electronics"},
        {"title": "Product B", "normalized_price": 150, "category": "electronics"},
        {"title": "Product C", "normalized_price": 200, "category": "electronics"},
        {"title": "Product D", "normalized_price": 80, "category": "electronics"},
        {"title": "Product E", "normalized_price": 300, "category": "electronics"},
        {"title": "Product F", "normalized_price": 120, "category": "electronics"},
        {"title": "Product G", "normalized_price": 180, "category": "electronics"},
        {"title": "Product H", "normalized_price": 90, "category": "electronics"},
        {"title": "Product I", "normalized_price": 250, "category": "electronics"},
        {"title": "Product J", "normalized_price": 110, "category": "electronics"},
        # Add some outliers
        {
            "title": "Expensive Product",
            "normalized_price": 1000,
            "category": "electronics",
        },
        {"title": "Cheap Product", "normalized_price": 10, "category": "electronics"},
    ]

    from scraper.analytics.price_analyzer import PriceAnalyzer

    analyzer = PriceAnalyzer()
    analysis = analyzer.analyze_prices(sample_data)

    print(f"📈 Basic Statistics:")
    print(f"   Count: {analysis.basic_stats['count']}")
    print(f"   Mean: ${analysis.basic_stats['mean']:.2f}")
    print(f"   Median: ${analysis.basic_stats['median']:.2f}")
    print(f"   Standard Deviation: ${analysis.basic_stats['std']:.2f}")
    print(f"   Min: ${analysis.basic_stats['min']:.2f}")
    print(f"   Max: ${analysis.basic_stats['max']:.2f}")
    print(f"   Coefficient of Variation: {analysis.basic_stats['cv']:.2f}")

    print(f"\n📊 Distribution Analysis:")
    print(f"   Distribution Type: {analysis.price_distribution['distribution_type']}")
    print(f"   Price Ranges:")
    for segment, range_str in analysis.price_distribution["price_ranges"][
        "segments"
    ].items():
        print(f"     {segment.title()}: {range_str}")

    print(f"\n🚨 Outlier Detection:")
    print(f"   Outliers Found: {len(analysis.outliers)}")
    for outlier in analysis.outliers[:3]:  # Show first 3 outliers
        print(
            f"     {outlier['title']}: ${outlier['price']:.2f} (Z-score: {outlier['z_score']:.2f})"
        )

    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(analysis.recommendations[:3], 1):
        print(f"   {i}. {rec}")


def demo_full_scraping_workflow():
    """Demonstrate the complete scraping workflow with all features."""
    print_section("COMPLETE SCRAPING WORKFLOW")

    # Use a simple test URL that we know works
    test_url = "https://httpbin.org/html"
    config = load_config()

    print(f"🎯 Target URL: {test_url}")
    print(
        f"⚙️  Configuration loaded: {len(config.get('user_agents', []))} user agents, {len(config.get('proxies', []))} proxies"
    )

    try:
        # Initialize scraper
        scraper = Scraper(test_url, config)

        # Run full workflow
        print(f"\n🔄 Starting full scraping workflow...")
        results = scraper.fetch_data(
            enable_smart_detection=True, enable_enrichment=True, enable_analysis=True
        )

        # Display results
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Results Summary:")
        print(f"   Raw data items: {len(results['raw_data'])}")
        print(f"   Enriched data items: {len(results['enriched_data'])}")
        print(f"   Processing time: {results['stats']['processing_time']:.2f}s")
        print(f"   Requests made: {results['stats']['requests_made']}")
        print(f"   Successful requests: {results['stats']['successful_requests']}")

        if results["site_profile"]:
            print(f"   Site type: {results['site_profile'].site_type}")
            print(f"   Detection confidence: {results['site_profile'].confidence:.2f}")

        if results["enrichment_result"]:
            print(
                f"   Data quality score: {results['enrichment_result'].quality_score:.2f}"
            )

        if results["price_analysis"]:
            print(f"   Price outliers found: {len(results['price_analysis'].outliers)}")

        # Generate comprehensive report
        report = scraper.get_scraping_report()
        print(f"\n📋 Comprehensive Report Generated")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"demo_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"💾 Report saved to: {report_file}")

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        log_message("ERROR", f"Demo scraping failed: {e}")


def main():
    """Main demo function."""
    print_banner()

    # Setup logging
    setup_logging("logs/demo.log")
    log_message("INFO", "Advanced demo started")

    try:
        # Run all demos
        demo_smart_detection()
        demo_data_enrichment()
        demo_price_analysis()
        demo_full_scraping_workflow()

        print_section("DEMO COMPLETED")
        print("🎉 All advanced features demonstrated successfully!")
        print("\n💡 What you've seen:")
        print("   • Smart site detection with automatic configuration")
        print("   • Advanced data enrichment with contact extraction")
        print("   • Statistical price analysis with outlier detection")
        print("   • Complete scraping workflow with comprehensive reporting")
        print("\n🚀 Ready to use the enhanced scraper for your projects!")

        log_message("INFO", "Advanced demo completed successfully")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        log_message("ERROR", f"Demo failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
