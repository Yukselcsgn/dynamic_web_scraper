# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Modular anti-bot / fetch strategy.

Defaults favor polite, site-adaptive behavior: plain HTTP first, escalation
only when the site profile or HTTP response indicates stronger measures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

MODE_ORDER = {"minimal": 0, "balanced": 1, "stealth": 2, "aggressive": 3}
ORDER_TO_MODE = {v: k for k, v in MODE_ORDER.items()}


def _tier_from_site(site_profile: Any) -> int:
    """How strongly we should escalate based on detection alone (0 = none)."""
    if site_profile is None:
        return 0
    tier = 0
    if getattr(site_profile, "use_selenium", False):
        tier = max(tier, MODE_ORDER["stealth"])
    measures = getattr(site_profile, "anti_bot_measures", None) or []
    rs = getattr(site_profile, "recommended_settings", None) or {}
    if rs.get("cloudflare_protection") or "cloudflare" in measures:
        tier = max(tier, MODE_ORDER["balanced"])
    if any(m in ("captcha", "recaptcha") for m in measures):
        tier = max(tier, MODE_ORDER["balanced"])
    return tier


@dataclass
class AntiBotStrategy:
    """
    User-tunable fetch / anti-bot behavior.

    ``mode`` is the baseline; when ``adapt_to_site`` is True, the effective tier
    is max(mode, site-suggested tier) so simple sites stay light while protected
    sites still get stronger tools.
    """

    mode: str = "minimal"
    adapt_to_site: bool = True
    plain_http_first: bool = True
    cloudflare_first: bool = False
    use_client_hints: bool = False
    human_delay_style: str = "light"  # none | light | full
    domain_profile_overrides: Dict[str, str] = field(default_factory=dict)
    browser_on_forbidden: bool = False  # if True, 403 may trigger browser (stealth+)

    @classmethod
    def from_config(cls, config: Optional[Dict]) -> AntiBotStrategy:
        cfg = config or {}
        ab = cfg.get("anti_bot") or {}
        raw_mode = (ab.get("mode") or "minimal").lower()
        if raw_mode not in MODE_ORDER:
            raw_mode = "minimal"

        cloudflare_first = bool(ab.get("cloudflare_first", raw_mode == "aggressive"))
        plain_http_first = bool(
            ab.get("plain_http_first", raw_mode != "aggressive")
        )

        if "use_client_hints" in ab:
            use_client_hints = bool(ab["use_client_hints"])
        else:
            use_client_hints = raw_mode in ("stealth", "aggressive")

        if "human_delay_style" in ab:
            human_delay_style = str(ab["human_delay_style"])
        else:
            if raw_mode == "minimal":
                human_delay_style = "none"
            elif raw_mode == "aggressive":
                human_delay_style = "full"
            else:
                human_delay_style = "light"

        domain_profile_overrides = dict(ab.get("domain_profile_overrides") or {})

        browser_on_forbidden = bool(
            ab.get(
                "browser_on_forbidden",
                MODE_ORDER[raw_mode] >= MODE_ORDER["stealth"],
            )
        )

        return cls(
            mode=raw_mode,
            adapt_to_site=bool(ab.get("adapt_to_site", True)),
            plain_http_first=plain_http_first,
            cloudflare_first=cloudflare_first,
            use_client_hints=use_client_hints,
            human_delay_style=human_delay_style,
            domain_profile_overrides=domain_profile_overrides,
            browser_on_forbidden=browser_on_forbidden,
        )

    def effective_mode(self, site_profile: Any) -> str:
        base = MODE_ORDER.get(self.mode, 0)
        if not self.adapt_to_site:
            return ORDER_TO_MODE[base]
        merged = max(base, _tier_from_site(site_profile))
        return ORDER_TO_MODE[merged]

    def profile_name_for_url(self, url: str, site_profile: Any) -> str:
        """Resolve StealthProfile dict key (minimal|balanced|stealth|aggressive)."""
        from urllib.parse import urlparse

        host = urlparse(url).netloc.lower()
        for domain_fragment, profile_name in self.domain_profile_overrides.items():
            if domain_fragment.lower() in host and profile_name in MODE_ORDER:
                return profile_name
        name = self.effective_mode(site_profile)
        return name if name in MODE_ORDER else "minimal"


def body_suggests_bot_challenge(text: str) -> bool:
    """Heuristic: HTML looks like a challenge / empty shell, not real content."""
    if not text:
        return True
    lower = text.lower()
    needles: List[str] = [
        "checking your browser",
        "ddos protection by cloudflare",
        "just a moment",
        "enable javascript",
        "turn javascript on",
        "cf-challenge",
        "challenge-platform",
        "attention required! | cloudflare",
        "unusual traffic from your computer",
        "robot check",
        "pardon our interruption",
    ]
    return any(n in lower for n in needles)
