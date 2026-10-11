"""Tests for JSON and CSV export engine."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from backend.exports import export_to_csv, export_to_json, save_export_file
from backend.servers.model import Server


class TestExportEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.servers = [
            Server(id="101", name='Alpha "DeFi" Guild', icon_url=None, owner=False, category="Crypto / DeFi"),
            Server(id="102", name="Zelda, Mario & Co.", icon_url="https://example.com/icon.png", owner=True, category="Gaming"),
        ]

    def test_export_to_json(self) -> None:
        json_str = export_to_json(self.servers)
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "101")
        self.assertEqual(parsed[0]["name"], 'Alpha "DeFi" Guild')
        self.assertFalse(parsed[0]["owner"])
        self.assertEqual(parsed[0]["category"], "Crypto / DeFi")
        self.assertIsNone(parsed[0]["icon_url"])

        # No credential or security fields leaked
        for record in parsed:
            self.assertEqual(set(record.keys()), {"id", "name", "owner", "category", "icon_url"})

    def test_export_to_csv(self) -> None:
        csv_str = export_to_csv(self.servers)
        reader = list(csv.DictReader(csv_str.splitlines()))
        self.assertEqual(len(reader), 2)

        # Escaped quotes and commas
        self.assertEqual(reader[0]["name"], 'Alpha "DeFi" Guild')
        self.assertEqual(reader[1]["name"], "Zelda, Mario & Co.")
        self.assertEqual(reader[1]["owner"], "True")
        self.assertEqual(reader[1]["icon_url"], "https://example.com/icon.png")

    def test_save_export_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "exports" / "test.json"
            content = export_to_json(self.servers)
            saved = save_export_file(file_path, content)
            self.assertTrue(saved.is_file())
            self.assertEqual(saved.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
