"""Tests for desktop window initialization and bridge methods."""
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import app
from backend.bridge import DesktopBridge


class TestDesktopWindow(unittest.TestCase):
    def test_frontend_index_path_exists(self) -> None:
        index_path = app.get_frontend_index_path()
        self.assertTrue(index_path.is_file(), f"{index_path} should exist")

    def test_app_icon_path_exists(self) -> None:
        icon_path = app.get_app_icon_path()
        self.assertIsNotNone(icon_path)
        self.assertTrue(icon_path.is_file(), f"{icon_path} should exist")
        self.assertTrue(str(icon_path).endswith("cleancord.ico"))


    def test_bridge_get_status(self) -> None:
        bridge = DesktopBridge()
        status = bridge.get_status()
        self.assertIsInstance(status, dict)
        self.assertEqual(status.get("status"), "online")
        self.assertEqual(status.get("app_name"), "CleanCord")
        self.assertEqual(status.get("mode"), "mock")


    @patch("webview.create_window")
    def test_create_window_calls_pywebview(self, mock_create_window: MagicMock) -> None:
        mock_window = MagicMock()
        mock_create_window.return_value = mock_window

        bridge = DesktopBridge()
        window = app.create_window(bridge)

        mock_create_window.assert_called_once()
        args, kwargs = mock_create_window.call_args
        self.assertEqual(kwargs.get("title"), app.APP_TITLE)
        self.assertEqual(kwargs.get("js_api"), bridge)
        self.assertEqual(kwargs.get("width"), app.DEFAULT_WIDTH)
        self.assertEqual(kwargs.get("height"), app.DEFAULT_HEIGHT)
        self.assertEqual(kwargs.get("min_size"), (app.MIN_WIDTH, app.MIN_HEIGHT))
        self.assertEqual(window, mock_window)

    @patch("webview.start")
    @patch("app.create_window")
    def test_main_passes_icon_to_webview_start(
        self,
        mock_create_window: MagicMock,
        mock_start: MagicMock,
    ) -> None:
        app.main()
        mock_create_window.assert_called_once()
        mock_start.assert_called_once()
        args, kwargs = mock_start.call_args
        self.assertIn("icon", kwargs)
        self.assertTrue(kwargs["icon"].endswith("cleancord.ico"))



    def test_bridge_query_and_selection(self) -> None:
        bridge = DesktopBridge()
        servers = bridge.get_servers(query="Elden")
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]["name"], "Elden Ring Community")

        # Validation eliminates owned server IDs
        owned_id = next(s["id"] for s in bridge.get_servers() if s["owner"])
        eligible = bridge.validate_selection([servers[0]["id"], owned_id])
        self.assertIn(servers[0]["id"], eligible)
        self.assertNotIn(owned_id, eligible)

        # Select all in filtered view excludes owned servers
        all_filtered = bridge.select_all_filtered()
        self.assertNotIn(owned_id, all_filtered)

    def test_bridge_export_methods(self) -> None:
        bridge = DesktopBridge()
        json_export = bridge.export_servers_json(query="Elden")
        self.assertIn("Elden Ring Community", json_export)

        csv_export = bridge.export_servers_csv(query="Elden")
        self.assertIn("Elden Ring Community", csv_export)
        self.assertIn("id,name,owner,category,icon_url", csv_export)

    def test_connect_token_validation(self) -> None:
        bridge = DesktopBridge()
        res_empty = bridge.connect_token("")
        self.assertFalse(res_empty["success"])
        self.assertIn("Token cannot be empty", res_empty["error"])

        # Invalid characters only should be stripped to empty and rejected
        res_invalid = bridge.connect_token("   $$$%%%   ")
        self.assertFalse(res_invalid["success"])
        self.assertIn("Token cannot be empty", res_invalid["error"])

    def test_bridge_preview_and_execute_cleanup(self) -> None:
        bridge = DesktopBridge()
        servers = bridge.get_servers()
        eligible_server = next(s for s in servers if not s["owner"])
        owned_server = next(s for s in servers if s["owner"])

        # Preview checks owner protection
        preview = bridge.preview_cleanup([eligible_server["id"], owned_server["id"]])
        self.assertEqual(preview["eligible_count"], 1)
        self.assertEqual(preview["protected_owner_count"], 1)

        # Execution leaves eligible server and removes it from list
        result = bridge.execute_cleanup([eligible_server["id"], owned_server["id"]])
        self.assertEqual(result["success_count"], 1)
        self.assertIn(eligible_server["id"], result["left_server_ids"])

        # Remaining servers no longer include the left server
        remaining_ids = [s["id"] for s in bridge.get_servers()]
        self.assertNotIn(eligible_server["id"], remaining_ids)
        self.assertIn(owned_server["id"], remaining_ids)


    @patch("backend.integrations.client.DiscordApiClient.fetch_all_guilds")
    @patch("requests.get")
    def test_connect_token_avatar_retrieval(
        self,
        mock_get: MagicMock,
        mock_guilds: MagicMock,
    ) -> None:
        mock_guilds.return_value = []
        bridge = DesktopBridge()

        # 1. Custom avatar returns CDN URL
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "id": "123456789",
            "username": "DiscordTester",
            "avatar": "abcdef123456",
        }
        mock_get.return_value = mock_resp

        res = bridge.connect_token("valid_token_123")
        self.assertTrue(res["success"])
        self.assertEqual(res["username"], "DiscordTester")
        self.assertEqual(
            res["avatar_url"],
            "https://cdn.discordapp.com/avatars/123456789/abcdef123456.png",
        )

        # 2. User without custom avatar returns avatar_url None (fallback D logo)
        mock_resp_no_avatar = MagicMock()
        mock_resp_no_avatar.ok = True
        mock_resp_no_avatar.json.return_value = {
            "id": "123456789",
            "username": "NoAvatarUser",
            "avatar": None,
        }
        mock_get.return_value = mock_resp_no_avatar

        res_no_avatar = bridge.connect_token("valid_token_123")
        self.assertTrue(res_no_avatar["success"])
        self.assertEqual(res_no_avatar["username"], "NoAvatarUser")
        self.assertIsNone(res_no_avatar["avatar_url"])


if __name__ == "__main__":
    unittest.main()


