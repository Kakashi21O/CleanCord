"""Normalized Server data model and validation."""
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Server:
    """Normalized Discord server representation.
    
    Invariants:
    - id must be a non-empty string.
    - name must be a non-empty string.
    - icon_url is optional string or None.
    - owner is boolean.
    - category is string.
    - Strictly excludes member counts, timestamps, channels, or messages.
    """
    id: str
    name: str
    icon_url: Optional[str]
    owner: bool
    category: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Server id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Server name must be a non-empty string")
        if not isinstance(self.owner, bool):
            raise TypeError("Server owner must be a boolean")
        if not isinstance(self.category, str):
            raise TypeError("Server category must be a string")
        if self.icon_url is not None and not isinstance(self.icon_url, str):
            raise TypeError("Server icon_url must be a string or None")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Server":
        """Construct a validated Server instance from a dictionary."""
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            icon_url=data.get("icon_url"),
            owner=bool(data.get("owner", False)),
            category=str(data.get("category", "Other")).strip() or "Other",
        )
