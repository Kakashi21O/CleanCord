"""Tests for DiscordApiClient with mocked network calls."""
import json
import unittest
from unittest.mock import MagicMock

from backend.integrations import DiscordApiClient, REQUEST_FAILED


class TestDiscordApiClient(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_opener = MagicMock()
        self.client = DiscordApiClient(
            token="test-token-xyz",
            rate_limit_pause=0.01,
            opener=self.mock_opener,
        )

    def test_token_required_for_requests(self) -> None:
        client_no_token = DiscordApiClient(token=None, opener=self.mock_opener)
        with self.assertRaises(ValueError):
            client_no_token.request("GET", "/users/@me")

    def test_get_current_user_success(self) -> None:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "id": "123456",
            "username": "TestUser",
            "discriminator": "0001",
        }).encode("utf-8")
        self.mock_opener.open.return_value.__enter__.return_value = mock_response

        user = self.client.get_current_user()
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "TestUser")
        self.assertEqual(user["id"], "123456")

    def test_fetch_all_guilds_pagination(self) -> None:
        # First page returns 200 guilds, second returns 50
        page1 = [{"id": f"guild_{i}", "name": f"Server {i}", "owner": False} for i in range(200)]
        page2 = [{"id": f"guild_{200 + i}", "name": f"Server {200 + i}", "owner": False} for i in range(50)]

        resp1 = MagicMock()
        resp1.status = 200
        resp1.read.return_value = json.dumps(page1).encode("utf-8")

        resp2 = MagicMock()
        resp2.status = 200
        resp2.read.return_value = json.dumps(page2).encode("utf-8")

        self.mock_opener.open.return_value.__enter__.side_effect = [resp1, resp2]

        guilds = self.client.fetch_all_guilds()
        self.assertEqual(len(guilds), 250)
        self.assertEqual(self.mock_opener.open.call_count, 2)

    def test_leave_guild_success(self) -> None:
        mock_response = MagicMock()
        mock_response.status = 204  # 204 No Content indicates success
        self.mock_opener.open.return_value.__enter__.return_value = mock_response

        success = self.client.leave_guild("987654")
        self.assertTrue(success)

    def test_leave_guild_empty_id(self) -> None:
        self.assertFalse(self.client.leave_guild(""))


if __name__ == "__main__":
    unittest.main()
