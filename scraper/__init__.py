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

"""Dynamic Web Scraper package (lazy exports for faster submodule imports)."""

from importlib import import_module
from typing import Any

from .config import load_config
from .logging_manager.logging_manager import log_message
from .user_agent_manager.user_agent_manager import UserAgentManager

__all__ = ["Scraper", "UserAgentManager", "log_message", "load_config", "main"]

_LAZY_EXPORTS = {
    "Scraper": (".core.scraper", "Scraper"),
    "main": (".main", "main"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        module_name, attr = _LAZY_EXPORTS[name]
        module = import_module(module_name, __package__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
