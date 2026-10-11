from typing import Any, Dict, List

from backend.servers.mock_data import MOCK_SERVERS


class DesktopBridge:
    """Safely exposes explicit Python backend methods to the frontend JS environment.
    
    Treats all incoming data from the webview context as untrusted.
    """

    def get_status(self) -> Dict[str, Any]:
        """Return system status and mode."""
        return {
            "status": "online",
            "app_name": "Server Prune",
            "mode": "mock",
        }

    def get_servers(self) -> List[Dict[str, Any]]:
        """Return normalized list of servers (mock data during foundation)."""
        return [dict(server) for server in MOCK_SERVERS]

