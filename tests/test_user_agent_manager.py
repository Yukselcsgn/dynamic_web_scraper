# tests/test_user_agent_manager.py

import pytest
from ..scraper.user_agent_manager.user_agent_manager import get_user_agent

def test_get_user_agent():
    # Kullanıcı ajanı alma fonksiyonunu test eder
    user_agent = get_user_agent()
    assert isinstance(user_agent, str), "Kullanıcı ajanı bir string olmalı."
    assert len(user_agent) > 0, "Boş bir kullanıcı ajanı döndü."
