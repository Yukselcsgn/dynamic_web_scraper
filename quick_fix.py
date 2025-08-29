#!/usr/bin/env python3
"""
Quick fix script to address immediate issues
"""

import json
import os
import sys


def fix_corrupted_files():
    """Fix corrupted JSON files."""
    print("🔧 Fixing corrupted files...")

    # Fix jobs.json.backup
    jobs_backup_path = "data/job_queue/jobs.json.backup"
    if os.path.exists(jobs_backup_path):
        try:
            with open(jobs_backup_path, "r") as f:
                content = f.read().strip()
                if not content or content == "":
                    print("📝 Fixing empty jobs.json.backup...")
                    with open(jobs_backup_path, "w") as f:
                        json.dump([], f)
                    print("✅ jobs.json.backup fixed")
                else:
                    json.loads(content)  # Test if valid JSON
                    print("✅ jobs.json.backup is valid")
        except json.JSONDecodeError:
            print("📝 Fixing corrupted jobs.json.backup...")
            with open(jobs_backup_path, "w") as f:
                json.dump([], f)
            print("✅ jobs.json.backup fixed")
        except Exception as e:
            print(f"⚠️  Error checking jobs.json.backup: {e}")

    # Ensure jobs.json is valid
    jobs_path = "data/job_queue/jobs.json"
    if os.path.exists(jobs_path):
        try:
            with open(jobs_path, "r") as f:
                json.load(f)  # Test if valid JSON
            print("✅ jobs.json is valid")
        except json.JSONDecodeError:
            print("📝 Fixing corrupted jobs.json...")
            with open(jobs_path, "w") as f:
                json.dump([], f)
            print("✅ jobs.json fixed")
        except Exception as e:
            print(f"⚠️  Error checking jobs.json: {e}")


def check_undetected_chromedriver():
    """Check if undetected-chromedriver is available."""
    print("\n🔍 Checking undetected-chromedriver availability...")

    try:
        import undetected_chromedriver as uc

        print("✅ undetected-chromedriver is available")
        return True
    except ImportError:
        print("❌ undetected-chromedriver is not installed")
        print("💡 To install: python install_undetected_chromedriver.py")
        return False


def create_debug_directory():
    """Create debug directory if it doesn't exist."""
    print("\n📁 Creating debug directory...")

    debug_dir = "debug_html"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
        print(f"✅ Created {debug_dir} directory")
    else:
        print(f"✅ {debug_dir} directory already exists")


def main():
    """Main function."""
    print("🚀 Quick Fix Script")
    print("=" * 30)

    # Fix corrupted files
    fix_corrupted_files()

    # Check undetected-chromedriver
    undetected_available = check_undetected_chromedriver()

    # Create debug directory
    create_debug_directory()

    print("\n📊 Summary:")
    print("=" * 30)
    print("✅ Corrupted files fixed")
    print("✅ Debug directory ready")

    if undetected_available:
        print("✅ undetected-chromedriver available")
        print("\n🎉 All systems ready! You can run the scraper now.")
    else:
        print("⚠️  undetected-chromedriver not available")
        print("💡 Run: python install_undetected_chromedriver.py")
        print("🔄 The scraper will use standard Selenium as fallback.")

    print("\n🚀 You can now run the scraper with:")
    print("   python scraper/main.py")


if __name__ == "__main__":
    main()
