"""Normalization service converting raw Discord API guild objects to Server models."""
from typing import Any, Dict, List, Optional

from backend.servers.categorizer import infer_category
from backend.servers.model import Server


def normalize_discord_guild(raw_guild: Dict[str, Any]) -> Optional[Server]:
    """Convert raw Discord API guild dictionary to normalized Server model.
    
    Invariants:
    - Discord guild ID must be string.
    - Owner flag must be extracted safely from boolean.
    - Icon URL formatted to CDN url if present.
    - Excludes channels, member counts, and timestamps.
    """
    raw_id = raw_guild.get("id")
    raw_name = raw_guild.get("name")
    if not raw_id or not raw_name:
        return None

    guild_id = str(raw_id).strip()
    name = str(raw_name).strip()
    if not guild_id or not name:
        return None

    icon_hash = raw_guild.get("icon")
    icon_url = None
    if icon_hash:
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.png"

    owner = bool(raw_guild.get("owner", False))
    category = infer_category(name)

    return Server(
        id=guild_id,
        name=name,
        icon_url=icon_url,
        owner=owner,
        category=category,
    )


def normalize_guilds_batch(raw_guilds: List[Dict[str, Any]]) -> List[Server]:
    """Normalize a collection of raw guild dictionaries."""
    normalized: List[Server] = []
    for g in raw_guilds:
        server = normalize_discord_guild(g)
        if server is not None:
            normalized.append(server)
    return normalized
