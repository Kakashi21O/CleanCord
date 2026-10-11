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

    def get_servers(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        ascending: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return filtered and sorted list of servers."""
        filtered = self._servers
        if query or category:
            from backend.servers.service import filter_servers
            filtered = filter_servers(filtered, query=query, category=category)
        
        from backend.servers.service import sort_servers
        sorted_list = sort_servers(filtered, ascending=ascending)
        return [server.to_dict() for server in sorted_list]

    def validate_selection(self, selected_ids: List[str]) -> List[str]:
        """Validate proposed selection against owner protection rules.
        
        Returns strictly eligible (non-owned) server IDs.
        """
        from backend.servers.service import compute_eligible_selection
        eligible = compute_eligible_selection(self._servers, set(selected_ids))
        return list(eligible)

    def select_all_filtered(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[str]:
        """Return IDs of all eligible servers in the current filter scope."""
        from backend.servers.service import filter_servers, select_all_eligible
        filtered = filter_servers(self._servers, query=query, category=category)
        return list(select_all_eligible(filtered))

    def export_servers_json(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        ascending: bool = True,
    ) -> str:
        """Export currently filtered/sorted servers as JSON string."""
        from backend.exports import export_to_json
        from backend.servers.service import filter_servers, sort_servers

        filtered = filter_servers(self._servers, query=query, category=category)
        sorted_list = sort_servers(filtered, ascending=ascending)
        return export_to_json(sorted_list)

    def export_servers_csv(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        ascending: bool = True,
    ) -> str:
        """Export currently filtered/sorted servers as CSV string."""
        from backend.exports import export_to_csv
        from backend.servers.service import filter_servers, sort_servers

        filtered = filter_servers(self._servers, query=query, category=category)
        sorted_list = sort_servers(filtered, ascending=ascending)
        return export_to_csv(sorted_list)

