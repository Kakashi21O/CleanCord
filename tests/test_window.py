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


if __name__ == "__main__":
    unittest.main()

