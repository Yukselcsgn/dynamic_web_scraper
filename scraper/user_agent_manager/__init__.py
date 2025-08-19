"""
User-agent management for the dynamic e-commerce scraper project.

Modules:
- user_agent_manager: Manages user-agent selection and rotation.
- user_agent_loader: Loads user-agent strings from files.
"""

# Import main user-agent functionalities
from .user_agent_manager import UserAgentManager

__all__ = ["UserAgentManager"]
