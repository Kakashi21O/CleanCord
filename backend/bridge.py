"""Bridge API exposed to pywebview frontend."""
from typing import Any, Dict


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
