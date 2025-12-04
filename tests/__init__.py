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
Dynamic Web Scraper Test Suite

This package contains comprehensive tests for all scraper functionality.
Organized by feature modules for easy navigation and maintenance.
"""

__version__ = "2.0.0"
__author__ = "Dynamic Web Scraper Team"

# Test categories
__all__ = [
    # Core functionality tests
    "test_core",
    # Feature-specific test modules
    "test_analytics",
    "test_anti_bot",
    "test_comparison",
    "test_dashboard",
    "test_data_processing",
    "test_distributed",
    "test_export",
    "test_plugins",
    "test_reporting",
    "test_site_detection",
    "test_utils",
    # Integration and end-to-end tests
    "test_integration",
    "test_e2e",
    # Performance and stress tests
    "test_performance",
    "test_stress",
]
