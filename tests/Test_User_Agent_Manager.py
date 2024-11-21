import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from unittest.mock import patch, MagicMock
from scraper.user_agent_manager.user_agent_manager import UserAgentManager


class TestUserAgentManager(unittest.TestCase):
    @patch("user_agent_manager.load_user_agents_from_file")
    def test_load_user_agents_from_file_success(self, mock_load_user_agents):
        """Test that UserAgentManager loads user agents from a file successfully."""
        mock_user_agents = ["Agent1", "Agent2", "Agent3"]
        mock_load_user_agents.return_value = mock_user_agents

        manager = UserAgentManager(source="file", file_path="mock_path")
        self.assertEqual(manager.user_agents, mock_user_agents)
        self.assertEqual(len(manager.user_agents), 3)

    @patch("user_agent_manager.load_user_agents_from_file")
    def test_load_user_agents_from_file_empty_list(self, mock_load_user_agents):
        """Test handling of an empty user agent list loaded from file."""
        mock_load_user_agents.return_value = []

        with self.assertRaises(ValueError) as context:
            UserAgentManager(source="file", file_path="mock_path")
        self.assertEqual(str(context.exception), "Yüklenen kullanıcı ajanı listesi boş!")

    @patch("user_agent_manager.load_user_agents_from_api")
    def test_load_user_agents_from_api_success(self, mock_load_user_agents):
        """Test that UserAgentManager loads user agents from an API successfully."""
        mock_user_agents = ["Agent1", "Agent2", "Agent3"]
        mock_load_user_agents.return_value = mock_user_agents

        manager = UserAgentManager(source="api", api_url="mock_api_url")
        self.assertEqual(manager.user_agents, mock_user_agents)
        self.assertEqual(len(manager.user_agents), 3)

    @patch("user_agent_manager.load_user_agents_from_api")
    def test_load_user_agents_from_api_empty_list(self, mock_load_user_agents):
        """Test handling of an empty user agent list loaded from API."""
        mock_load_user_agents.return_value = []

        with self.assertRaises(ValueError) as context:
            UserAgentManager(source="api", api_url="mock_api_url")
        self.assertEqual(str(context.exception), "Yüklenen kullanıcı ajanı listesi boş!")

    def test_invalid_source(self):
        """Test handling of an invalid source type."""
        with self.assertRaises(ValueError) as context:
            UserAgentManager(source="invalid")
        self.assertEqual(str(context.exception), "Geçersiz kullanıcı ajanı kaynağı.")

    @patch("user_agent_manager.random.choice")
    def test_get_user_agent_success(self, mock_choice):
        """Test selecting a random user agent from the list."""
        mock_user_agents = ["Agent1", "Agent2", "Agent3"]
        manager = UserAgentManager(source="file", file_path="mock_path")
        manager.user_agents = mock_user_agents  # directly setting list for test

        mock_choice.return_value = "Agent2"
        selected_agent = manager.get_user_agent()

        self.assertEqual(selected_agent, "Agent2")
        mock_choice.assert_called_once_with(mock_user_agents)

    def test_get_user_agent_empty_list(self):
        """Test get_user_agent with an empty user agent list."""
        manager = UserAgentManager(source="file", file_path="mock_path")
        manager.user_agents = []  # directly setting an empty list for test

        with self.assertRaises(ValueError) as context:
            manager.get_user_agent()
        self.assertEqual(str(context.exception), "Kullanıcı ajanı listesi boş!")

    @patch("user_agent_manager.load_user_agents_from_file")
    def test_logging_on_load_success(self, mock_load_user_agents):
        """Test logging output on successful loading of user agents from a file."""
        mock_user_agents = ["Agent1", "Agent2", "Agent3"]
        mock_load_user_agents.return_value = mock_user_agents

        with self.assertLogs("user_agent_manager", level="INFO") as log:
            UserAgentManager(source="file", file_path="mock_path")
            self.assertIn("INFO:root:3 kullanıcı ajanı başarıyla yüklendi.", log.output)

    @patch("user_agent_manager.load_user_agents_from_file")
    def test_logging_on_load_failure(self, mock_load_user_agents):
        """Test logging output on failure to load user agents due to an empty list."""
        mock_load_user_agents.return_value = []

        with self.assertLogs("user_agent_manager", level="ERROR") as log:
            with self.assertRaises(ValueError):
                UserAgentManager(source="file", file_path="mock_path")
            self.assertIn("ERROR:root:Kullanıcı ajanları yüklenirken hata: Yüklenen kullanıcı ajanı listesi boş!", log.output)


if __name__ == "__main__":
    unittest.main()
