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
Anti-bot strategy selection.

Decides *how hard* the scraper should try for a given URL / site profile:

* ``minimal``    - plain HTTP only, escalate only when a challenge is detected
* ``balanced``   - plain HTTP first, Cloudflare bypass on challenge
* ``stealth``    - browser automation allowed
* ``aggressive`` - Cloudflare bypass first, browser automation allowed

The tiers are ordered (see ``MODE_ORDER``); a detected site profile can only
*raise* the configured tier, never lower it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlparse

MODE_ORDER = ("minimal", "balanced", "stealth", "aggressive")
DEFAULT_MODE = "minimal"

# Lower-case fragments that indicate a bot-challenge / interstitial page.
_CHALLENGE_MARKERS = (
    "checking your browser",
    "just a moment",
    "cf-challenge",
    "cf-browser-verification",
    "challenge-platform",
    "enable javascript",
)


def _tier(mode: str) -> int:
    return MODE_ORDER.index(mode)


def raise_tier(mode: str, minimum: str) -> str:
    """Return the higher of two tiers."""
    return mode if _tier(mode) >= _tier(minimum) else minimum


def body_suggests_bot_challenge(body: Optional[str]) -> bool:
    """
    Heuristic: does ``body`` look like a bot challenge instead of real content?

    An empty body is treated as a challenge, since blocked requests frequently
    return 200 with no content.
    """
    if not body or not body.strip():
        return True
    lowered = body.lower()
    return any(marker in lowered for marker in _CHALLENGE_MARKERS)


def _host_matches(host: str, domain: str) -> bool:
    domain = domain.lower().lstrip(".")
    return host == domain or host.endswith(f".{domain}")


@dataclass
class AntiBotStrategy:
    """Resolved anti-bot behaviour (built from ``config["anti_bot"]``)."""

    mode: str = DEFAULT_MODE
    plain_http_first: bool = True
    cloudflare_first: bool = False
    adapt_to_site: bool = True
    human_delay_style: str = "default"
    browser_on_forbidden: bool = False
    domain_profile_overrides: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: Optional[Mapping[str, Any]]) -> "AntiBotStrategy":
        """
        Build a strategy from a scraper config dict.

        Unknown modes fall back to ``minimal``. ``plain_http_first`` and
        ``cloudflare_first`` default from the mode unless set explicitly.
        """
        section = (config or {}).get("anti_bot") or {}

        mode = section.get("mode", DEFAULT_MODE)
        if mode not in MODE_ORDER:
            mode = DEFAULT_MODE

        overrides = {
            str(domain).lower(): name
            for domain, name in (section.get("domain_profile_overrides") or {}).items()
            if name in MODE_ORDER
        }

        aggressive = mode == "aggressive"
        return cls(
            mode=mode,
            plain_http_first=bool(section.get("plain_http_first", not aggressive)),
            cloudflare_first=bool(section.get("cloudflare_first", aggressive)),
            adapt_to_site=bool(section.get("adapt_to_site", True)),
            human_delay_style=str(section.get("human_delay_style", "default")),
            browser_on_forbidden=bool(
                section.get("browser_on_forbidden", mode in ("stealth", "aggressive"))
            ),
            domain_profile_overrides=overrides,
        )

    def effective_mode(self, site_profile: Any = None) -> str:
        """
        Tier to use for ``site_profile``.

        With ``adapt_to_site`` the tier is raised to at least ``balanced`` for
        Cloudflare-protected sites and ``stealth`` for sites needing a browser.
        """
        mode = self.mode
        if site_profile is None or not self.adapt_to_site:
            return mode

        measures = getattr(site_profile, "anti_bot_measures", None)
        settings = getattr(site_profile, "recommended_settings", None)
        cloudflare = (
            isinstance(measures, (list, tuple, set)) and "cloudflare" in measures
        ) or (
            isinstance(settings, dict) and settings.get("cloudflare_protection") is True
        )
        if cloudflare:
            mode = raise_tier(mode, "balanced")

        if getattr(site_profile, "use_selenium", False) is True:
            mode = raise_tier(mode, "stealth")

        return mode

    def domain_override(self, url: str) -> Optional[str]:
        """Profile name forced for ``url``'s domain, if any."""
        host = (urlparse(url).hostname or "").lower()
        for domain, name in self.domain_profile_overrides.items():
            if _host_matches(host, domain):
                return name
        return None

    def profile_name_for_url(self, url: str, site_profile: Any = None) -> str:
        """Profile name for ``url``: a domain override wins over adaptation."""
        return self.domain_override(url) or self.effective_mode(site_profile)
