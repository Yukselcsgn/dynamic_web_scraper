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
Proxy formatting helpers.

Converts a single proxy string (``host:port``, ``scheme://host:port`` or
``scheme://user:pass@host:port``) into the shapes required by ``requests``,
Selenium (Chrome) and Playwright, and provides credential masking so proxy
passwords never reach log files.
"""

import re
from dataclasses import dataclass
from typing import Dict, Optional
from urllib.parse import quote, unquote, urlsplit

# Matches "scheme://user:password@" anywhere inside free text (e.g. exception
# messages coming from urllib3/requests that embed the proxy URL).
_CREDENTIALS_RE = re.compile(r"(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)(?P<user>[^:@/\s]+):(?P<pwd>[^@/\s]+)@")

_DEFAULT_SCHEME = "http"


def _mask_username(username: str) -> str:
    """Keep at most the first two characters of a username."""
    return f"{username[:2]}***" if username else ""


def redact_proxy_credentials(text: str) -> str:
    """
    Mask ``user:password@`` fragments in arbitrary text.

    Safe to call on exception messages before logging them.
    """
    return _CREDENTIALS_RE.sub(
        lambda m: f"{m.group('scheme')}{_mask_username(m.group('user'))}:***@", str(text)
    )


@dataclass(frozen=True)
class ProxyEndpoint:
    """Parsed proxy with helpers for each client library."""

    scheme: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def has_auth(self) -> bool:
        return bool(self.username)

    @property
    def server(self) -> str:
        """Proxy URL without credentials."""
        return f"{self.scheme}://{self.host}:{self.port}"

    def masked(self) -> str:
        """Proxy URL that is safe to log."""
        if self.has_auth:
            return f"{self.scheme}://{_mask_username(self.username)}:***@{self.host}:{self.port}"
        return self.server

    def __repr__(self) -> str:  # never expose the password via repr()/logging
        return f"ProxyEndpoint({self.masked()})"

    def requests_proxies(self) -> Dict[str, str]:
        """``proxies=`` mapping for requests (credentials included)."""
        if self.has_auth:
            auth = f"{quote(self.username, safe='')}:{quote(self.password or '', safe='')}"
            url = f"{self.scheme}://{auth}@{self.host}:{self.port}"
        else:
            url = self.server
        return {"http": url, "https": url}

    def chrome_argument(self) -> str:
        """
        ``--proxy-server`` argument for Chrome.

        Chrome ignores credentials embedded in this flag, so only the
        credential-free server is passed (see ``has_auth``).
        """
        return f"--proxy-server={self.server}"

    def playwright_proxy(self) -> Dict[str, str]:
        """``proxy=`` mapping for ``browser_type.launch`` / ``new_context``."""
        proxy: Dict[str, str] = {"server": self.server}
        if self.has_auth:
            proxy["username"] = self.username
            proxy["password"] = self.password or ""
        return proxy


def parse_proxy(raw: str) -> ProxyEndpoint:
    """
    Parse a proxy string into a ``ProxyEndpoint``.

    Raises:
        ValueError: If the string has no host or port. The message never
            contains the raw value, so it cannot leak credentials.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Empty proxy string")

    candidate = raw.strip()
    if "://" not in candidate:
        candidate = f"{_DEFAULT_SCHEME}://{candidate}"

    try:
        parts = urlsplit(candidate)
        host, port = parts.hostname, parts.port
    except ValueError as exc:
        raise ValueError("Malformed proxy string") from exc

    if not host or port is None:
        raise ValueError("Proxy must include host and port")

    return ProxyEndpoint(
        scheme=parts.scheme.lower(),
        host=host,
        port=port,
        username=unquote(parts.username) if parts.username else None,
        password=unquote(parts.password) if parts.password else None,
    )


def mask_proxy(raw: Optional[str]) -> str:
    """Return a log-safe representation of a proxy string (never raises)."""
    if not raw:
        return "None"
    try:
        return parse_proxy(raw).masked()
    except ValueError:
        return "<invalid proxy>"
