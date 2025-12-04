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
Customization Module

This module provides customization capabilities for the scraper, including
configuration management, user preferences, and extensibility features.
"""

from .config_manager import (
    ConfigManager,
    ScraperConfig,
    get_config,
    get_config_manager,
    get_setting,
    set_setting,
)

__all__ = [
    "ConfigManager",
    "ScraperConfig",
    "get_config_manager",
    "get_config",
    "get_setting",
    "set_setting",
]
