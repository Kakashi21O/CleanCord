"""Tests for mock server models and frontend assets."""
import re
import unittest
from pathlib import Path

from backend.bridge import DesktopBridge
from backend.servers.mock_data import MOCK_SERVERS


class TestStaticUI(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent

    def test_mock_servers_conform_to_architecture_spec(self) -> None:
        required_keys = {"id", "name", "icon_url", "owner", "category"}
        self.assertGreater(len(MOCK_SERVERS), 0)
        for s in MOCK_SERVERS:
            self.assertTrue(required_keys.issubset(s.keys()))
            self.assertIsInstance(s["id"], str, "Server ID must be a string")
            self.assertIsInstance(s["name"], str, "Server name must be a string")
            self.assertIsInstance(s["owner"], bool, "Server owner flag must be a boolean")
            self.assertIsInstance(s["category"], str, "Server category must be a string")

    def test_bridge_returns_mock_servers(self) -> None:
        bridge = DesktopBridge()
        servers = bridge.get_servers()
        self.assertEqual(len(servers), len(MOCK_SERVERS))
        self.assertTrue(any(s["owner"] is True for s in servers), "Should include an owned server")
        self.assertTrue(any(s["owner"] is False for s in servers), "Should include a non-owned server")

    def test_frontend_files_exist_and_contain_required_tokens(self) -> None:
        css_file = self.root / "frontend" / "styles.css"
        self.assertTrue(css_file.is_file())
        css_content = css_file.read_text(encoding="utf-8")

        # Check required design tokens from AI/ui-context.md
        required_tokens = [
            "--bg-base",
            "--bg-surface",
            "--bg-subtle",
            "--bg-hover",
            "--selection-bg",
            "--text-primary",
            "--text-secondary",
            "--text-muted",
            "--accent-primary",
            "--border-default",
            "--state-error",
            "--state-success",
            "--state-warning",
        ]
        for token in required_tokens:
            self.assertIn(token, css_content, f"Missing token {token} in styles.css")

    def test_frontend_html_structure(self) -> None:
        html_file = self.root / "frontend" / "index.html"
        self.assertTrue(html_file.is_file())
        html_content = html_file.read_text(encoding="utf-8")

        self.assertIn('id="search-input"', html_content)
        self.assertIn('id="category-chips"', html_content)
        self.assertIn('id="btn-select-all"', html_content)
        self.assertIn('id="btn-deselect-all"', html_content)
        self.assertIn('id="server-list"', html_content)
        self.assertIn('id="btn-preview-cleanup"', html_content)

    def test_login_ui_structure(self) -> None:
        html_file = self.root / "frontend" / "index.html"
        html_content = html_file.read_text(encoding="utf-8")

        self.assertIn('id="login-view"', html_content)
        self.assertIn('id="app-view"', html_content)
        self.assertIn('id="input-token-main"', html_content)
        self.assertIn('Login with Token', html_content)
        self.assertIn('Discord User Token', html_content)
        self.assertIn('id="chk-remember-me"', html_content)
        self.assertIn('Remember me', html_content)
        self.assertNotIn('id="input-email"', html_content)
        self.assertNotIn('id="input-password"', html_content)
        self.assertNotIn('id="tab-btn-email"', html_content)
        self.assertNotIn('id="tab-btn-token"', html_content)

    def test_slide_over_menu_structure(self) -> None:
        html_file = self.root / "frontend" / "index.html"
        html_content = html_file.read_text(encoding="utf-8")

        self.assertIn('id="btn-menu-trigger"', html_content)
        self.assertIn('id="side-menu"', html_content)
        self.assertIn('id="menu-btn-refresh"', html_content)
        self.assertIn('id="menu-btn-logout"', html_content)
        self.assertIn('About CleanCord', html_content)
        self.assertIn('vj-m/CleanCord', html_content)
        self.assertNotIn('id="btn-switch-account"', html_content)


if __name__ == "__main__":
    unittest.main()
