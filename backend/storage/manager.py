"""Local storage managers for user preferences and whitelist.

Stores non-sensitive data in local JSON files.
Never stores tokens, credentials, or session data.
"""
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


@dataclass
class UserPreferences:
    """Application preferences with sensible defaults."""
    window_width: int = 960
    window_height: int = 700
    sort_ascending: bool = True
    selected_category: str = "ALL"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        return cls(
            window_width=int(data.get("window_width", 960)),
            window_height=int(data.get("window_height", 700)),
            sort_ascending=bool(data.get("sort_ascending", True)),
            selected_category=str(data.get("selected_category", "ALL")),
        )


class StorageManager:
    """Safely manages reading and writing to local JSON files."""

    def __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None:
        if base_dir is None:
            self.base_dir = Path.home() / ".cleancord"
        else:
            self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_path = self.base_dir / "preferences.json"
        self.whitelist_path = self.base_dir / "whitelist.json"

    def load_preferences(self) -> UserPreferences:
        """Load user preferences, falling back gracefully to defaults on error."""
        if not self.preferences_path.is_file():
            return UserPreferences()
        try:
            content = self.preferences_path.read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, dict):
                return UserPreferences.from_dict(data)
        except Exception:
            pass
        return UserPreferences()

    def save_preferences(self, preferences: UserPreferences) -> None:
        """Save preferences to local JSON file."""
        try:
            content = json.dumps(preferences.to_dict(), indent=2)
            self.preferences_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to save preferences: {e}") from e

    def load_whitelist(self) -> Set[str]:
        """Load whitelist set of server IDs (strings)."""
        if not self.whitelist_path.is_file():
            return set()
        try:
            content = self.whitelist_path.read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, list):
                return {str(item).strip() for item in data if str(item).strip()}
        except Exception:
            pass
        return set()

    def save_whitelist(self, server_ids: Set[str]) -> None:
        """Save whitelist set of server IDs."""
        try:
            sorted_ids = sorted(str(sid) for sid in server_ids)
            content = json.dumps(sorted_ids, indent=2)
            self.whitelist_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to save whitelist: {e}") from e
