"""Export serialization services for JSON and CSV."""
import csv
import io
import json
from pathlib import Path
from typing import Iterable, List, Union

from backend.servers.model import Server

EXPORT_FIELDS: List[str] = ["id", "name", "owner", "category", "icon_url"]


def export_to_json(servers: Iterable[Server], indent: int = 2) -> str:
    """Serialize servers to clean UTF-8 JSON string.
    
    Invariants:
    - Strictly serializes only EXPORT_FIELDS.
    - Never includes credentials, tokens, or session IDs.
    """
    records = []
    for s in servers:
        records.append({
            "id": s.id,
            "name": s.name,
            "owner": s.owner,
            "category": s.category,
            "icon_url": s.icon_url,
        })
    return json.dumps(records, indent=indent, ensure_ascii=False)


def export_to_csv(servers: Iterable[Server]) -> str:
    """Serialize servers to standard CSV string with RFC 4180 escaping.
    
    Invariants:
    - Strictly serializes only EXPORT_FIELDS.
    - Preserves UTF-8 and escapes commas/quotes properly.
    """
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=EXPORT_FIELDS,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writeheader()
    for s in servers:
        writer.writerow({
            "id": s.id,
            "name": s.name,
            "owner": s.owner,
            "category": s.category,
            "icon_url": s.icon_url if s.icon_url is not None else "",
        })
    return output.getvalue()


def save_export_file(file_path: Union[str, Path], content: str) -> Path:
    """Safely write export content to file with UTF-8 encoding."""
    path = Path(file_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
