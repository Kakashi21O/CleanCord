"""Tests for cleanup safety rules, preview generation, and execution."""
import unittest

from backend.cleanup import (
    CleanupPreview,
    CleanupResult,
    execute_server_cleanup,
    generate_cleanup_preview,
)
from backend.servers.model import Server


class TestCleanupService(unittest.TestCase):
    def setUp(self) -> None:
        self.s1 = Server(id="101", name="DeFi Alpha", icon_url=None, owner=False, category="Crypto / DeFi")
        self.s2 = Server(id="102", name="Owned Server", icon_url=None, owner=True, category="Development")
        self.s3 = Server(id="103", name="Whitelisted Gaming", icon_url=None, owner=False, category="Gaming")
        self.s4 = Server(id="104", name="General Chat", icon_url=None, owner=False, category="Other")
        self.servers = [self.s1, self.s2, self.s3, self.s4]

    def test_preview_enforces_owner_and_whitelist_safeguards(self) -> None:
        selected_ids = {"101", "102", "103", "104"}
        whitelist_ids = {"103"}

        preview = generate_cleanup_preview(self.servers, selected_ids, whitelist_ids)

        self.assertEqual(preview.total_requested, 4)
        self.assertEqual(preview.eligible_count, 2)  # 101 and 104
        self.assertEqual(preview.protected_owner_count, 1)  # 102
        self.assertEqual(preview.whitelisted_count, 1)  # 103

        leave_ids = [s["id"] for s in preview.servers_to_leave]
        self.assertIn("101", leave_ids)
        self.assertIn("104", leave_ids)
        self.assertNotIn("102", leave_ids)
        self.assertNotIn("103", leave_ids)

    def test_execute_server_cleanup(self) -> None:
        # Mock leave_fn tracking calls
        left_ids = []

        def mock_leave(sid: str) -> bool:
            left_ids.append(sid)
            return True

        selected_ids = {"101", "102", "104"}  # Includes owned server 102
        result = execute_server_cleanup(self.servers, selected_ids, leave_fn=mock_leave)

        # 102 should be rejected by safety check and never passed to leave_fn
        self.assertEqual(result.total_attempted, 2)
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(set(result.left_server_ids), {"101", "104"})
        self.assertNotIn("102", left_ids)

    def test_execute_server_cleanup_handles_failures(self) -> None:
        def mock_leave_fail(sid: str) -> bool:
            return sid == "101"

        selected_ids = {"101", "104"}
        result = execute_server_cleanup(self.servers, selected_ids, leave_fn=mock_leave_fail)

        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.failed_count, 1)
        self.assertEqual(result.left_server_ids, ["101"])
        self.assertEqual(result.failed_server_ids, ["104"])


if __name__ == "__main__":
    unittest.main()
