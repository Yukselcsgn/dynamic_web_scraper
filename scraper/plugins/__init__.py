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
Plugin System Module

This module provides a plugin system for extending the scraper with custom
functionality, allowing users to add their own data processors, validators,
and custom scraping logic.
"""

from .plugin_manager import (
    BasePlugin,
    CustomScraperPlugin,
    DataProcessorPlugin,
    PluginInfo,
    PluginManager,
    ValidatorPlugin,
)

__all__ = [
    "PluginManager",
    "BasePlugin",
    "DataProcessorPlugin",
    "ValidatorPlugin",
    "CustomScraperPlugin",
    "PluginInfo",
]
