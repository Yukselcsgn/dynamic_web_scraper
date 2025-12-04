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
Proxy management package for handling proxy settings and rotations.

Modules:
- proxy_manager: Main proxy management functionalities.
- proxy_loader: Loads proxy lists from files.
- proxy_rotator: Handles proxy rotation logic.
- proxy_validator: Validates the functionality of proxies.
"""

# Import proxy manager components
from .proxy_manager import ProxyManager
from .proxy_rotator import ProxyRotator

__all__ = ["ProxyManager", "ProxyRotator"]
