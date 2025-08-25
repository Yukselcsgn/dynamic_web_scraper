#!/usr/bin/env python3
"""
Test Runner for Dynamic Web Scraper

This script provides organized test execution with different test categories
and reporting capabilities.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_pytest_command(args, test_path=None):
    """Run pytest with given arguments."""
    cmd = ["python", "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.quiet:
        cmd.append("-q")

    if args.coverage:
        cmd.extend(["--cov=scraper", "--cov-report=html", "--cov-report=term"])

    if args.html:
        cmd.extend(["--html=test_reports/report.html", "--self-contained-html"])

    if args.junit:
        cmd.append("--junitxml=test_reports/junit.xml")

    if args.parallel:
        cmd.extend(["-n", "auto"])

    if args.stop_on_failure:
        cmd.append("-x")

    if args.max_failures:
        cmd.extend(["--maxfail", str(args.max_failures)])

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_specific_test_category(category, args):
    """Run tests for a specific category."""
    test_categories = {
        "core": "tests/core/",
        "analytics": "tests/analytics/",
        "anti_bot": "tests/anti_bot/",
        "comparison": "tests/comparison/",
        "dashboard": "tests/dashboard/",
        "data_processing": "tests/data_processing/",
        "distributed": "tests/distributed/",
        "export": "tests/export/",
        "plugins": "tests/plugins/",
        "reporting": "tests/reporting/",
        "site_detection": "tests/site_detection/",
        "utils": "tests/utils/",
        "integration": "tests/integration/",
        "e2e": "tests/e2e/",
        "performance": "tests/performance/",
        "stress": "tests/stress/",
    }

    if category not in test_categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return 1

    test_path = test_categories[category]
    print(f"🧪 Running {category} tests...")
    return run_pytest_command(args, test_path)


def run_all_tests(args):
    """Run all tests."""
    print("🧪 Running all tests...")
    return run_pytest_command(args)


def run_quick_tests(args):
    """Run quick tests (unit tests only)."""
    print("⚡ Running quick tests (unit tests only)...")
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "-m",
        "not integration and not e2e and not performance and not stress",
    ]

    if args.verbose:
        cmd.append("-v")

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_integration_tests(args):
    """Run integration tests only."""
    print("🔗 Running integration tests...")
    cmd = ["python", "-m", "pytest", "tests/", "-m", "integration"]

    if args.verbose:
        cmd.append("-v")

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_performance_tests(args):
    """Run performance tests only."""
    print("⚡ Running performance tests...")
    cmd = ["python", "-m", "pytest", "tests/", "-m", "performance"]

    if args.verbose:
        cmd.append("-v")

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def create_test_report_directory():
    """Create test report directory."""
    report_dir = project_root / "test_reports"
    report_dir.mkdir(exist_ok=True)
    return report_dir


def generate_test_summary():
    """Generate a summary of available tests."""
    test_dirs = [
        "tests/core/",
        "tests/analytics/",
        "tests/anti_bot/",
        "tests/comparison/",
        "tests/dashboard/",
        "tests/data_processing/",
        "tests/distributed/",
        "tests/export/",
        "tests/plugins/",
        "tests/reporting/",
        "tests/site_detection/",
        "tests/utils/",
        "tests/integration/",
        "tests/e2e/",
        "tests/performance/",
        "tests/stress/",
    ]

    print("📋 Available Test Categories:")
    print("=" * 50)

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            test_files = [
                f
                for f in os.listdir(test_dir)
                if f.startswith("test_") and f.endswith(".py")
            ]
            print(f"✅ {test_dir}: {len(test_files)} test files")
        else:
            print(f"❌ {test_dir}: Not found")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Dynamic Web Scraper Test Runner")

    # Test selection
    parser.add_argument("--category", "-c", help="Run tests for specific category")
    parser.add_argument(
        "--quick", "-q", action="store_true", help="Run quick tests only (unit tests)"
    )
    parser.add_argument(
        "--integration", "-i", action="store_true", help="Run integration tests only"
    )
    parser.add_argument(
        "--performance", "-p", action="store_true", help="Run performance tests only"
    )
    parser.add_argument("--all", "-a", action="store_true", help="Run all tests")

    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--html", action="store_true", help="Generate HTML test report")
    parser.add_argument(
        "--junit", action="store_true", help="Generate JUnit XML report"
    )

    # Execution options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--stop-on-failure", "-x", action="store_true", help="Stop on first failure"
    )
    parser.add_argument(
        "--max-failures", type=int, help="Maximum number of failures before stopping"
    )

    # Other options
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available test categories"
    )
    parser.add_argument(
        "--setup", "-s", action="store_true", help="Setup test environment"
    )

    args = parser.parse_args()

    # Create test report directory
    create_test_report_directory()

    # List available tests
    if args.list:
        generate_test_summary()
        return 0

    # Setup test environment
    if args.setup:
        print("🔧 Setting up test environment...")
        # Add any test environment setup here
        print("✅ Test environment setup complete")
        return 0

    # Determine which tests to run
    if args.category:
        return run_specific_test_category(args.category, args)
    elif args.quick:
        return run_quick_tests(args)
    elif args.integration:
        return run_integration_tests(args)
    elif args.performance:
        return run_performance_tests(args)
    elif args.all:
        return run_all_tests(args)
    else:
        # Default: run quick tests
        return run_quick_tests(args)


if __name__ == "__main__":
    print("🧪 Dynamic Web Scraper Test Runner")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    exit_code = main()

    print()
    print("=" * 50)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")

    sys.exit(exit_code)
