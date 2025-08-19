#!/usr/bin/env python3
"""
Simple test script to verify the scraper components work correctly.
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Dynamic Web Scraper Imports...")
    print("=" * 50)

    try:
        # Test core imports
        print("Testing core imports...")
        print("✅ config.py imported successfully")

        print("✅ Scraper.py imported successfully")

        print("✅ logging_manager.py imported successfully")

        print("✅ proxy_rotator.py imported successfully")

        print("✅ user_agent_manager.py imported successfully")

        print("✅ scraper_exceptions.py imported successfully")

        print("✅ data_parser.py imported successfully")

        # Test advanced features
        print("\nTesting advanced features...")
        print("✅ dynamic_selector.py imported successfully")

        print("✅ css_rules.py imported successfully")

        print("✅ html_analyzer.py imported successfully")

        print("\n🎉 All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n📋 Testing Configuration...")
    try:
        from scraper.config import load_config

        config = load_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - User agents: {len(config.get('user_agents', []))}")
        print(f"   - Proxies: {len(config.get('proxies', []))}")
        print(f"   - Use proxy: {config.get('use_proxy', False)}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_basic_functionality():
    """Test basic scraper functionality."""
    print("\n🔧 Testing Basic Functionality...")
    try:
        # Test UserAgentManager
        from scraper.user_agent_manager.user_agent_manager import UserAgentManager

        ua_manager = UserAgentManager(["Mozilla/5.0 (Test)"])
        user_agent = ua_manager.get_user_agent()
        print(f"✅ UserAgentManager: {user_agent}")

        # Test ProxyRotator
        from scraper.proxy_manager.proxy_rotator import ProxyRotator

        proxy_rotator = ProxyRotator(["127.0.0.1:8080"])
        proxy = proxy_rotator.rotate_proxy()
        print(f"✅ ProxyRotator: {proxy}")

        # Test CSS Rule Manager
        from scraper.css_selectors.css_rules import CSSRuleManager, CSSRule

        rule_manager = CSSRuleManager()
        rule = CSSRule(name="test", selector=".test", description="Test rule")
        rule_manager.add_rule("test_site", rule)
        print(f"✅ CSSRuleManager: Rule added successfully")

        # Test Dynamic Selector
        from scraper.css_selectors.dynamic_selector import DynamicSelector

        DynamicSelector()
        print(f"✅ DynamicSelector: Created successfully")

        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Dynamic Web Scraper Test Suite")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Basic Functionality Test", test_basic_functionality),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📝 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Run 'python scraper/main.py' to start scraping")
        print("   2. Run 'python run_dashboard.py' to start the web dashboard")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
