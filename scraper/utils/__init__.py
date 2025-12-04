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
Utility functions for the dynamic e-commerce scraper project.

Modules:
- request_utils: Utilities for handling requests.
- parse_utils: Utilities for parsing data.
- wait_utils: Utilities for managing waits and delays.
- user_agent_utils: Utilities for handling user-agent strings.
- proxy_utils: Utilities for managing proxy settings.
"""

# Import key utilities for easier access
from .request_utils import send_request

__all__ = ["send_request"]
