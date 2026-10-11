"""Server queries, local searching, sorting, and selection helpers."""
from typing import Callable, Iterable, List, Optional, Set

from backend.servers.model import Server


def filter_servers(
    servers: Iterable[Server],
    query: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Server]:
    """Filter servers by case-insensitive name/ID query and category."""
    results: List[Server] = []
    clean_query = query.strip().lower() if query else ""
    target_category = category.strip() if category and category != "ALL" else None

    for server in servers:
        if target_category and server.category != target_category:
            continue
        if clean_query:
            match_name = clean_query in server.name.lower()
            match_id = clean_query in server.id.lower()
            if not match_name and not match_id:
                continue
        results.append(server)

    return results


def sort_servers(servers: Iterable[Server], ascending: bool = True) -> List[Server]:
    """Sort servers alphabetically by server name."""
    return sorted(
        servers,
        key=lambda s: s.name.casefold(),
        reverse=not ascending,
    )


def compute_eligible_selection(
    servers: Iterable[Server],
    target_ids: Set[str],
) -> Set[str]:
    """Given a target set of IDs, return only IDs that are eligible (non-owned).
    
    Protects owned servers from ever being selected.
    """
    eligible_ids: Set[str] = set()
    for server in servers:
        if server.id in target_ids and not server.owner:
            eligible_ids.add(server.id)
    return eligible_ids


def select_all_eligible(servers: Iterable[Server]) -> Set[str]:
    """Select all eligible (non-owner) servers in the provided collection."""
    return {server.id for server in servers if not server.owner}
