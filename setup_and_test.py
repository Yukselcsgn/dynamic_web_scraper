#!/usr/bin/env python3
"""
Setup and test script for the Dynamic Web Scraper.
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_directories():
    """Create necessary directories."""
    print("📁 Creating necessary directories...")

    directories = ["data", "logs", "data/processed_data"]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")


def test_scraper():
    """Test the scraper with a simple example."""
    print("\n🧪 Testing scraper functionality...")

    try:
        # Import required modules
        from scraper.config import load_config
        from scraper.Scraper import Scraper
        from scraper.logging_manager.logging_manager import setup_logging, log_message

        # Setup logging
        setup_logging("logs/scraper.log")
        log_message("INFO", "Scraper test started")

        # Load configuration
        config = load_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - User agents: {len(config.get('user_agents', []))}")
        print(f"   - Proxies: {len(config.get('proxies', []))}")
        print(f"   - Use proxy: {config.get('use_proxy', False)}")

        # Test URL (a simple, safe test URL)
        test_url = "https://httpbin.org/html"
        print(f"\n🌐 Testing with URL: {test_url}")

        # Create scraper instance
        scraper = Scraper(test_url, config)
        print("✅ Scraper instance created successfully")

        # Test data fetching
        print("📡 Fetching data...")
        data = scraper.fetch_data()

        if data:
            print(f"✅ Data fetched successfully! Found {len(data)} items")
            print(f"   Sample data: {data[:2]}")  # Show first 2 items

            # Test saving data
            output_file = "data/test_output.csv"
            scraper.save_data(data, output_file, "csv")
            print(f"✅ Data saved to: {output_file}")
        else:
            print("⚠️  No data found, but scraper is working correctly")

        log_message("INFO", "Scraper test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        log_message("ERROR", f"Scraper test failed: {e}")
        return False


def main():
    """Main setup and test function."""
    print("🚀 Dynamic Web Scraper Setup and Test")
    print("=" * 50)

    # Setup directories
    setup_directories()

    # Test scraper
    success = test_scraper()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup and test completed successfully!")
        print("\n💡 You can now:")
        print("   1. Run 'python scraper/main.py' to start scraping")
        print("   2. Run 'python run_dashboard.py' to start the web dashboard")
        print("   3. Edit config.json to customize settings")
    else:
        print("❌ Setup and test failed. Please check the errors above.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
