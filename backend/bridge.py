from typing import Any, Dict, List, Optional

from backend.servers.categorizer import infer_category
from backend.servers.mock_data import MOCK_SERVERS
from backend.servers.model import Server


class DesktopBridge:
    """Safely exposes explicit Python backend methods to the frontend JS environment.
    
    Treats all incoming data from the webview context as untrusted.
    """

    def __init__(self, raw_servers: Optional[List[Dict[str, Any]]] = None) -> None:
        raw_list = raw_servers if raw_servers is not None else MOCK_SERVERS
        self._servers = [
            Server(
                id=str(s["id"]),
                name=str(s["name"]),
                icon_url=s.get("icon_url"),
                owner=bool(s.get("owner", False)),
                category=s.get("category") or infer_category(s["name"]),
            )
            for s in raw_list
        ]

    def get_status(self) -> Dict[str, Any]:
        """Return system status and mode."""
        return {
            "status": "online",
            "app_name": "Server Prune",
            "mode": "mock",
        }

    def get_servers(self) -> List[Dict[str, Any]]:
        """Return normalized list of servers."""
        return [server.to_dict() for server in self._servers]

