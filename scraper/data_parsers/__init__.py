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
Data parsers for the dynamic e-commerce scraper project.

Modules:
- data_parser: Base parser for data extraction.
- html_parser: HTML-specific data parsing functionality.
"""

# Import parsers for easier access
from .data_parser import save_data
from .html_parser import parse_html

__all__ = ["save_data", "parse_html"]
