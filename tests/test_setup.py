"""Tests for project structure and baseline invariants."""
import unittest
from pathlib import Path


class TestProjectSetup(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent

    def test_required_directories_exist(self) -> None:
        self.assertTrue((self.root / "backend").is_dir(), "backend directory should exist")
        self.assertTrue((self.root / "tests").is_dir(), "tests directory should exist")
        self.assertTrue((self.root / "AI").is_dir(), "AI directory should exist")

    def test_requirements_file_exists(self) -> None:
        req_file = self.root / "requirements.txt"
        self.assertTrue(req_file.is_file(), "requirements.txt should exist")
        content = req_file.read_text(encoding="utf-8")
        self.assertIn("pywebview", content)

    def test_gitignore_protects_env_and_caches(self) -> None:
        gitignore = self.root / ".gitignore"
        self.assertTrue(gitignore.is_file(), ".gitignore should exist")
        content = gitignore.read_text(encoding="utf-8")
        self.assertIn(".env", content)
        self.assertIn("__pycache__", content)


if __name__ == "__main__":
    unittest.main()
