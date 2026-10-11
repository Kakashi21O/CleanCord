"""Local category inference using name pattern keywords.

Runs strictly locally without making external network requests.
Categorization patterns reference runesleo/discord-cleanup keywords.
"""
from typing import Dict, List

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Crypto / DeFi": [
        "airdrop", "defi", "swap", "bridge", "zk", "layer", "l2", "arb",
        "starknet", "scroll", "linea", "blast", "zora", "eigen", "ethena",
        "pendle", "crypto", "solana", "eth", "bitcoin", "btc", "wallet",
    ],
    "NFT": [
        "nft", "ape", "punk", "azuki", "doodle", "art", "mint", "opensea",
        "magic eden", "pfp", "collectible",
    ],
    "Development": [
        "dev", "hack", "build", "github", "code", "coding", "sdk", "api",
        "software", "python", "rust", "typescript", "javascript", "developer",
        "programming", "linux", "backend", "frontend",
    ],
    "Gaming": [
        "game", "gaming", "guild", "play", "quest", "axie", "steam", "rpg",
        "esports", "minecraft", "roblox", "valorant", "fortnite", "elden ring",
        "clan", "mmo",
    ],
    "Trading": [
        "trade", "trading", "signal", "alpha", "whale", "dex", "perp",
        "futures", "stocks", "forex", "wallstreet",
    ],
    "Anime": [
        "anime", "manga", "otaku", "genshin", "honkai", "waifu", "vtuber",
        "weeb", "cosplay",
    ],
}


def infer_category(server_name: str) -> str:
    """Infer category from server name pattern matching.
    
    Returns standard category or 'Other' if no pattern matches.
    """
    if not server_name:
        return "Other"

    name_lower = server_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return category

    return "Other"
