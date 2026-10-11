"""Discord API client implementing safe, rate-limited communication.

References runesleo/discord-cleanup for endpoint structure, Windows SSL handling,
pagination, and status verification.
Zero external network libraries — uses standard library urllib.request.
"""
import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

API_BASE = "https://discord.com/api/v10"
REQUEST_FAILED = object()
LEAVE_PAYLOAD = {"lurking": False}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class DiscordApiClient:
    """Handles communication with Discord REST API v10."""

    def __init__(
        self,
        token: Optional[str] = None,
        rate_limit_pause: float = 1.0,
        opener: Optional[urllib.request.OpenerDirector] = None,
    ) -> None:
        import re

        clean_token = re.sub(r"[^a-zA-Z0-9._-]", "", token) if token else None
        self.token = clean_token if clean_token else None
        self.rate_limit_pause = rate_limit_pause
        self.opener = opener or self._build_opener()

    @staticmethod
    def _build_opener() -> urllib.request.OpenerDirector:
        """Create SSL context loading system trust certs for Windows compatibility."""
        context = ssl.create_default_context()
        context.load_default_certs()
        return urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))

    def _headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "X-Discord-Locale": "en-US",
        }
        if self.token:
            headers["Authorization"] = self.token
        return headers

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Any:
        """Execute HTTP request against Discord API with rate limiting handling."""
        if not self.token:
            raise ValueError("Discord token is required for API requests")

        url = f"{API_BASE}{endpoint}"
        headers = self._headers()
        payload_bytes = None

        if data is not None:
            headers["Content-Type"] = "application/json"
            payload_bytes = json.dumps(data).encode("utf-8")

        for attempt in range(1, max_retries + 1):
            req = urllib.request.Request(
                url=url,
                data=payload_bytes,
                headers=headers,
                method=method,
            )
            try:
                with self.opener.open(req) as resp:
                    if resp.status == 204:
                        return None
                    raw_body = resp.read()
                    return json.loads(raw_body.decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    try:
                        err_body = json.loads(e.read().decode("utf-8"))
                        retry_after = float(err_body.get("retry_after", 1.0))
                    except Exception:
                        retry_after = 1.0
                    time.sleep(retry_after)
                    continue
                elif e.code == 401:
                    raise PermissionError("Invalid or unauthorized Discord token")
                else:
                    return REQUEST_FAILED
            except urllib.error.URLError:
                if attempt < max_retries:
                    time.sleep(1.0)
                    continue
                return REQUEST_FAILED

        return REQUEST_FAILED

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Fetch current user profile to verify token validity."""
        result = self.request("GET", "/users/@me")
        if result is REQUEST_FAILED or not isinstance(result, dict):
            return None
        return result

    def fetch_all_guilds(self) -> List[Dict[str, Any]]:
        """Paginate and fetch all guilds the user is in.
        
        Extracts only required server metadata fields (id, name, icon, owner).
        """
        all_guilds: List[Dict[str, Any]] = []
        after: Optional[str] = None

        while True:
            endpoint = "/users/@me/guilds?limit=200"
            if after:
                endpoint += f"&after={after}"

            batch = self.request("GET", endpoint)
            if batch is REQUEST_FAILED or not isinstance(batch, list) or not batch:
                break

            all_guilds.extend(batch)
            if len(batch) < 200:
                break
            after = batch[-1].get("id")

        return all_guilds

    def leave_guild(self, guild_id: str) -> bool:
        """Leave a server. Returns True on verified 204 response."""
        clean_id = str(guild_id).strip()
        if not clean_id:
            return False

        endpoint = f"/users/@me/guilds/{clean_id}"
        result = self.request("DELETE", endpoint, data=LEAVE_PAYLOAD)
        return result is None
