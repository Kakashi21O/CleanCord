"""Tests for Server data model, categorizer, and server query services."""
import unittest

from backend.servers.categorizer import infer_category
from backend.servers.model import Server
from backend.servers.service import (
    compute_eligible_selection,
    filter_servers,
    select_all_eligible,
    sort_servers,
)


class TestServerServices(unittest.TestCase):
    def setUp(self) -> None:
        self.s1 = Server(id="101", name="Alpha DeFi Hub", icon_url=None, owner=False, category="Crypto / DeFi")
        self.s2 = Server(id="102", name="Zelda Game Club", icon_url=None, owner=False, category="Gaming")
        self.s3 = Server(id="103", name="My Owned Dev Guild", icon_url=None, owner=True, category="Development")
        self.s4 = Server(id="104", name="General Coffee", icon_url=None, owner=False, category="Other")
        self.servers = [self.s1, self.s2, self.s3, self.s4]

    def test_server_model_validation(self) -> None:
        # Valid conversion
        d = self.s1.to_dict()
        self.assertEqual(d["id"], "101")
        self.assertEqual(d["name"], "Alpha DeFi Hub")
        self.assertFalse(d["owner"])

        # String ID invariant
        reconstructed = Server.from_dict(d)
        self.assertEqual(reconstructed, self.s1)

        # Invalid ID raises ValueError
        with self.assertRaises(ValueError):
            Server(id="", name="Valid", icon_url=None, owner=False, category="Other")

        # Invalid name raises ValueError
        with self.assertRaises(ValueError):
            Server(id="123", name=" ", icon_url=None, owner=False, category="Other")

        # Invalid owner type raises TypeError
        with self.assertRaises(TypeError):
            Server(id="123", name="Test", icon_url=None, owner="true", category="Other")  # type: ignore

    def test_category_inference(self) -> None:
        self.assertEqual(infer_category("Ethereum DeFi & Yield"), "Crypto / DeFi")
        self.assertEqual(infer_category("CyberPunks NFT Drop"), "NFT")
        self.assertEqual(infer_category("Python Code & SDK Devs"), "Development")
        self.assertEqual(infer_category("Elden Ring Gaming Guild"), "Gaming")
        self.assertEqual(infer_category("Whale Trading Signals"), "Trading")
        self.assertEqual(infer_category("Genshin Impact Anime Lounge"), "Anime")
        self.assertEqual(infer_category("Just Hanging Out"), "Other")
        self.assertEqual(infer_category(""), "Other")

    def test_filter_servers_by_query_and_category(self) -> None:
        # Search by name
        results = filter_servers(self.servers, query="defi")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "101")

        # Search by ID
        results = filter_servers(self.servers, query="103")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "My Owned Dev Guild")

        # Filter by Category
        results = filter_servers(self.servers, category="Gaming")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "102")

        # Combined search and category
        results = filter_servers(self.servers, query="Alpha", category="Crypto / DeFi")
        self.assertEqual(len(results), 1)
        results_none = filter_servers(self.servers, query="Alpha", category="Gaming")
        self.assertEqual(len(results_none), 0)

    def test_sort_servers_alphabetical(self) -> None:
        # A to Z
        sorted_asc = sort_servers(self.servers, ascending=True)
        self.assertEqual(
            [s.name for s in sorted_asc],
            ["Alpha DeFi Hub", "General Coffee", "My Owned Dev Guild", "Zelda Game Club"],
        )

        # Z to A
        sorted_desc = sort_servers(self.servers, ascending=False)
        self.assertEqual(
            [s.name for s in sorted_desc],
            ["Zelda Game Club", "My Owned Dev Guild", "General Coffee", "Alpha DeFi Hub"],
        )

    def test_owner_protection_in_selection(self) -> None:
        # Attempt to select owned server (103) along with 101 and 102
        target_ids = {"101", "102", "103"}
        eligible = compute_eligible_selection(self.servers, target_ids)
        self.assertIn("101", eligible)
        self.assertIn("102", eligible)
        self.assertNotIn("103", eligible, "Owned server 103 must never be eligible for selection")

        # select_all_eligible should also exclude 103
        all_eligible = select_all_eligible(self.servers)
        self.assertEqual(all_eligible, {"101", "102", "104"})
        self.assertNotIn("103", all_eligible)


if __name__ == "__main__":
    unittest.main()
