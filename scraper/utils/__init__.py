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

__all__ = ['send_request']

