"""Tests for local JSON storage of preferences and whitelist."""
import tempfile
import unittest
from pathlib import Path

from backend.storage import StorageManager, UserPreferences


class TestStorageManager(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.storage = StorageManager(base_dir=self.tmpdir.name)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_default_preferences_when_no_file_exists(self) -> None:
        prefs = self.storage.load_preferences()
        self.assertEqual(prefs.window_width, 960)
        self.assertEqual(prefs.window_height, 700)
        self.assertTrue(prefs.sort_ascending)
        self.assertEqual(prefs.selected_category, "ALL")

    def test_save_and_load_preferences(self) -> None:
        custom_prefs = UserPreferences(
            window_width=1200,
            window_height=800,
            sort_ascending=False,
            selected_category="Gaming",
        )
        self.storage.save_preferences(custom_prefs)

        loaded = self.storage.load_preferences()
        self.assertEqual(loaded.window_width, 1200)
        self.assertEqual(loaded.window_height, 800)
        self.assertFalse(loaded.sort_ascending)
        self.assertEqual(loaded.selected_category, "Gaming")

    def test_malformed_preferences_recovers_to_defaults(self) -> None:
        self.storage.preferences_path.write_text("invalid json contents", encoding="utf-8")
        recovered = self.storage.load_preferences()
        self.assertEqual(recovered.window_width, 960)

    def test_whitelist_persistence(self) -> None:
        self.assertEqual(self.storage.load_whitelist(), set())

        ids = {"1001", "1002", "1005"}
        self.storage.save_whitelist(ids)

        loaded = self.storage.load_whitelist()
        self.assertEqual(loaded, ids)

    def test_malformed_whitelist_recovers_gracefully(self) -> None:
        self.storage.whitelist_path.write_text("{not a list}", encoding="utf-8")
        self.assertEqual(self.storage.load_whitelist(), set())


class TestWindowsCredentialStore(unittest.TestCase):
    def test_credential_store_save_get_delete(self) -> None:
        import sys
        from backend.storage import WindowsCredentialStore

        if sys.platform != "win32":
            self.skipTest("Windows-only test")

        test_target = "CleanCord_Unit_Test_Target"
        store = WindowsCredentialStore(target_name=test_target)

        # Ensure clean state
        store.delete_credential()
        self.assertIsNone(store.get_credential())

        # Save credential
        saved = store.save_credential("secret_discord_token_test_abc123")
        self.assertTrue(saved)

        # Retrieve credential
        retrieved = store.get_credential()
        self.assertEqual(retrieved, "secret_discord_token_test_abc123")

        # Delete credential
        deleted = store.delete_credential()
        self.assertTrue(deleted)
        self.assertIsNone(store.get_credential())

    def test_bridge_logout_clears_credential(self) -> None:
        from unittest.mock import MagicMock
        from backend.bridge import DesktopBridge

        mock_store = MagicMock()
        mock_store.get_credential.return_value = "saved_token"

        bridge = DesktopBridge(credential_store=mock_store)
        saved = bridge.get_saved_credential()
        self.assertTrue(saved["has_saved"])
        self.assertEqual(saved["token"], "saved_token")

        logout_res = bridge.logout()
        self.assertTrue(logout_res["success"])
        mock_store.delete_credential.assert_called_once()


if __name__ == "__main__":
    unittest.main()
