#!/usr/bin/env python3
# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Script to install undetected-chromedriver for enhanced browser automation
"""

import os
import subprocess
import sys


def install_undetected_chromedriver():
    """Install undetected-chromedriver package."""
    print("🔧 Installing undetected-chromedriver for enhanced browser automation...")

    try:
        # Try to install undetected-chromedriver
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "undetected-chromedriver"],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ undetected-chromedriver installed successfully!")
        print("📋 Installation output:")
        print(result.stdout)

        # Test the installation
        try:
            import undetected_chromedriver as uc

            print("✅ Import test successful - undetected-chromedriver is ready to use!")
            return True
        except ImportError as e:
            print(f"❌ Import test failed: {e}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("📋 Error output:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}")
        return False


def check_current_installation():
    """Check if undetected-chromedriver is already installed."""
    try:
        import undetected_chromedriver as uc

        print("✅ undetected-chromedriver is already installed!")
        return True
    except ImportError:
        print("⚠️  undetected-chromedriver is not installed")
        return False


def main():
    """Main function."""
    print("🚀 Undetected ChromeDriver Installation Script")
    print("=" * 50)

    # Check current installation
    if check_current_installation():
        print("\n🎉 undetected-chromedriver is ready to use!")
        return

    print("\n📦 Installing undetected-chromedriver...")
    success = install_undetected_chromedriver()

    if success:
        print("\n🎉 Installation completed successfully!")
        print("💡 The scraper will now use undetected-chromedriver for better stealth.")
        print("🔄 You can now run the scraper again with enhanced browser automation.")
    else:
        print("\n❌ Installation failed!")
        print("💡 You can try installing manually:")
        print("   pip install undetected-chromedriver")
        print("⚠️  The scraper will fall back to standard Selenium.")


if __name__ == "__main__":
    main()
