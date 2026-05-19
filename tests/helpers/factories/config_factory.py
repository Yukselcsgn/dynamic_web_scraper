"""Build config dicts for tests."""

from __future__ import annotations

from typing import Any, Dict, Optional


def make_config(
    *,
    anti_bot_mode: str = "minimal",
    adapt_to_site: bool = True,
    plain_http_first: Optional[bool] = None,
    cloudflare_first: Optional[bool] = None,
    domain_profile_overrides: Optional[Dict[str, str]] = None,
    user_agents: Optional[list] = None,
    **extra: Any,
) -> Dict[str, Any]:
    config: Dict[str, Any] = {
        "user_agents": user_agents
        or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ],
        "proxies": [],
        "use_proxy": False,
        "anti_bot": {
            "mode": anti_bot_mode,
            "adapt_to_site": adapt_to_site,
            **(
                {"plain_http_first": plain_http_first}
                if plain_http_first is not None
                else {}
            ),
            **(
                {"cloudflare_first": cloudflare_first}
                if cloudflare_first is not None
                else {}
            ),
            "human_delay_style": "none",
            "browser_on_forbidden": anti_bot_mode in ("stealth", "aggressive"),
            "domain_profile_overrides": domain_profile_overrides or {},
        },
    }
    config.update(extra)
    return config
