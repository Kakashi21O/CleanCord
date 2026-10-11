"""Cleanup safety validation, preview generation, and execution services."""
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Set

from backend.servers.model import Server


@dataclass(frozen=True)
class CleanupPreview:
    """Safe pre-flight preview of proposed server leaves."""
    total_requested: int
    eligible_count: int
    protected_owner_count: int
    whitelisted_count: int
    servers_to_leave: List[Dict[str, Any]]
    servers_protected: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CleanupResult:
    """Verified execution outcomes."""
    total_attempted: int
    success_count: int
    failed_count: int
    left_server_ids: List[str]
    failed_server_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def generate_cleanup_preview(
    servers: List[Server],
    selected_ids: Set[str],
    whitelist_ids: Optional[Set[str]] = None,
) -> CleanupPreview:
    """Inspect servers and generate pre-flight dry-run plan.
    
    Invariants:
    - Owned servers (owner == True) can NEVER be left.
    - Whitelisted servers are excluded from removal.
    """
    whitelisted = whitelist_ids or set()
    server_map = {s.id: s for s in servers}

    to_leave: List[Dict[str, Any]] = []
    protected: List[Dict[str, Any]] = []
    owner_count = 0
    whitelist_count = 0

    for sid in sorted(selected_ids):
        server = server_map.get(sid)
        if not server:
            continue

        if server.owner:
            owner_count += 1
            protected.append({
                "id": server.id,
                "name": server.name,
                "reason": "Owner protected",
            })
        elif server.id in whitelisted:
            whitelist_count += 1
            protected.append({
                "id": server.id,
                "name": server.name,
                "reason": "Whitelisted",
            })
        else:
            to_leave.append({
                "id": server.id,
                "name": server.name,
                "category": server.category,
            })

    return CleanupPreview(
        total_requested=len(selected_ids),
        eligible_count=len(to_leave),
        protected_owner_count=owner_count,
        whitelisted_count=whitelist_count,
        servers_to_leave=to_leave,
        servers_protected=protected,
    )


def execute_server_cleanup(
    servers: List[Server],
    selected_ids: Set[str],
    leave_fn: Callable[[str], bool],
    whitelist_ids: Optional[Set[str]] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> CleanupResult:
    """Execute confirmed server leave operations.
    
    Invariants:
    - Double checks owner protection immediately before invoking leave_fn.
    - Accurately tracks successful and failed operations.
    """
    preview = generate_cleanup_preview(servers, selected_ids, whitelist_ids)
    eligible_servers = preview.servers_to_leave

    success_ids: List[str] = []
    failed_ids: List[str] = []
    total = len(eligible_servers)

    for idx, item in enumerate(eligible_servers, 1):
        sid = item["id"]
        name = item["name"]

        if progress_callback:
            progress_callback(idx, total, name)

        try:
            ok = leave_fn(sid)
            if ok:
                success_ids.append(sid)
            else:
                failed_ids.append(sid)
        except Exception:
            failed_ids.append(sid)

    return CleanupResult(
        total_attempted=total,
        success_count=len(success_ids),
        failed_count=len(failed_ids),
        left_server_ids=success_ids,
        failed_server_ids=failed_ids,
    )
