from typing import Any, Dict, List, Optional, Set

from backend.servers.categorizer import infer_category
from backend.servers.mock_data import MOCK_SERVERS
from backend.servers.model import Server


class DesktopBridge:
    """Safely exposes explicit Python backend methods to the frontend JS environment.
    
    Treats all incoming data from the webview context as untrusted.
    """

    def __init__(
        self,
        raw_servers: Optional[List[Dict[str, Any]]] = None,
        api_client: Optional[Any] = None,
    ) -> None:
        self.api_client = api_client
        self.mode = "live" if api_client is not None else "mock"
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

    def connect_token(self, token: str) -> Dict[str, Any]:
        """Validate token and fetch user servers in live mode."""
        import re

        clean_token = re.sub(r"[^a-zA-Z0-9._-]", "", token) if token else ""
        if not clean_token:
            return {"success": False, "error": "Token cannot be empty or contain invalid characters"}

        import requests

        avatar_url = None
        username = "Unknown"

        try:
            response = requests.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": clean_token},
                timeout=10,
            )
            if response.ok:
                user = response.json()
                username = user.get("username", "Unknown")
                user_id = user.get("id")
                avatar_hash = user.get("avatar")
                if user_id and avatar_hash:
                    avatar_url = (
                        f"https://cdn.discordapp.com/avatars/"
                        f"{user_id}/{avatar_hash}.png"
                    )
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid or expired Discord token"}
            else:
                return {"success": False, "error": "Invalid or expired Discord token"}
        except requests.RequestException:
            # If request fails, fall back to client verification or return error
            return {"success": False, "error": "Failed to connect to Discord API"}

        from backend.integrations.client import DiscordApiClient
        from backend.servers.normalizer import normalize_guilds_batch

        client = DiscordApiClient(token=clean_token)
        raw_guilds = client.fetch_all_guilds()
        normalized = normalize_guilds_batch(raw_guilds)

        self.api_client = client
        self.mode = "live"
        self._servers = normalized

        return {
            "success": True,
            "username": username,
            "avatar_url": avatar_url,
            "server_count": len(self._servers),
            "mode": self.mode,
        }


    def get_status(self) -> Dict[str, Any]:
        """Return system status and mode."""
        return {
            "status": "online",
            "app_name": "CleanCord",
            "mode": getattr(self, "mode", "mock"),
        }



    def refresh_servers(self) -> List[Dict[str, Any]]:
        """Fetch fresh server list from Discord API in live mode, or reset mock servers."""
        if self.mode == "live" and self.api_client is not None:
            from backend.servers.normalizer import normalize_guilds_batch
            raw_guilds = self.api_client.fetch_all_guilds()
            self._servers = normalize_guilds_batch(raw_guilds)
        return [server.to_dict() for server in self._servers]

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

    def preview_cleanup(self, selected_ids: List[str]) -> Dict[str, Any]:

        """Generate safe pre-flight cleanup preview."""
        from backend.cleanup import generate_cleanup_preview

        whitelist_ids: Set[str] = set()
        if hasattr(self, "storage_manager") and self.storage_manager is not None:
            whitelist_ids = self.storage_manager.load_whitelist()

        preview = generate_cleanup_preview(self._servers, set(selected_ids), whitelist_ids)
        return preview.to_dict()

    def execute_cleanup(self, selected_ids: List[str]) -> Dict[str, Any]:
        """Execute cleanup on selected servers.
        
        In Demo mode, simulates verified departure.
        In Live mode, calls live Discord DELETE endpoint with rate limiting.
        """
        from backend.cleanup import execute_server_cleanup

        whitelist_ids: Set[str] = set()
        if hasattr(self, "storage_manager") and self.storage_manager is not None:
            whitelist_ids = self.storage_manager.load_whitelist()

        if self.mode == "live" and self.api_client:
            leave_fn = self.api_client.leave_guild
        else:
            # Demo/mock simulation
            leave_fn = lambda sid: True

        result = execute_server_cleanup(
            servers=self._servers,
            selected_ids=set(selected_ids),
            leave_fn=leave_fn,
            whitelist_ids=whitelist_ids,
        )

        # Remove successfully left servers from current in-memory view
        left_set = set(result.left_server_ids)
        self._servers = [s for s in self._servers if s.id not in left_set]

        return result.to_dict()


