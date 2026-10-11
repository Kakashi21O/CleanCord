# Discord Server Cleanup — Project Overview

## Overview

Discord Server Cleanup is a lightweight Windows desktop application for viewing, searching, selecting, and managing Discord servers through a clean, minimal interface. Built with Python, pywebview, and an HTML/CSS/JavaScript frontend, it emphasizes bulk selection, local categorization, data export, and safe cleanup workflows with minimal dependencies and API calls.

## Goals

1. **Responsive desktop UI:** View, search, and select Discord servers efficiently.
2. **Effortless discovery:** Instant search, alphabetical sorting, and category filters.
3. **Data portability:** Valid JSON and CSV exports without sensitive credentials.
4. **Local persistence:** Store user preferences and whitelist settings locally.
5. **Simplicity & safety:** Minimal dependencies, no extra API calls, and mandatory confirmation before any server-leave action.
6. **Robust packaging:** Distributable and testable Windows desktop application.

## Core Features & Requirements

### Server List
- **Fields displayed:** Server icon (or neutral placeholder), name, ID (string), owner status badge, and inferred category.
- **Explicit exclusions:** Never display or fetch member counts, server creation dates, join dates, channel lists, or message contents.
- **Row interaction:** Compact list with medium row spacing. Expandable row details for secondary info must be independent of selection checkboxes.

### Search, Sorting & Filters
- **Search:** Instant local matching by server name or ID.
- **Sorting:** Alphabetical by server name.
- **Categories:** Inferred locally from server names (never via extra API requests).
  - *Initial categories:* Gaming, Anime, Development, Crypto / DeFi, NFT, Trading, Other.
- Selections must be preserved across filter/search updates where practical.

### Selection Rules
- **Checkbox semantics:** Checked = selected to leave.
- **Owner protection:** Servers owned by the current user account can **never** be selected or left.
- **Bulk controls:** Select All / Deselect All operate on eligible servers within the current filtered view.

### JSON & CSV Export
- Exports full list or current filtered view.
- Fields: `id`, `name`, `owner`, `category`, `icon_url`.
- Standard UTF-8 encoding and proper CSV escaping. Must never contain tokens or credentials.

### Persistent Preferences
- Store non-sensitive settings locally (JSON): window geometry (size/position), sort preferences, UI settings.
- Malformed/missing settings must fail safely to defaults.

### Cleanup Workflow
- **Safety gate:** Actual server-leave actions remain disabled until an approved, supported authentication and API integration is confirmed.
- **Invariants:**
  - Launching the app must never trigger automated cleanup.
  - Mandatory preview and explicit user confirmation dialog before execution.
  - Revalidate server eligibility (especially owner protection) immediately before any execution.
  - Report exact verified outcomes (success/failed/skipped) and handle rate limits/network errors gracefully.

## Scope Boundaries

- **In Scope:** Windows desktop app (Python + pywebview + HTML/CSS/JS), light-themed compact server list, local search/sort/categorization, JSON/CSV export, local settings/whitelist, cleanup preview/safety verification, mocked tests, Windows packaging.
- **Out of Scope:** Fetching messages/channels/member counts/dates, deleting owned servers, transferring server ownership, background telemetry/analytics/cloud sync, bypassing Discord platform/API rules, executing real leave actions in automated tests.

## Technology Stack

| Layer | Technology | Role |
|---|---|---|
| Desktop | pywebview | Native desktop window |
| Frontend | HTML, CSS, JavaScript | Lightweight UI (Light theme, system fonts, CSS vars) |
| Backend | Python 3 | Core logic, data normalization, export, and bridge |
| Storage | Local JSON | Settings and whitelist persistence |
| Testing | unittest / pytest | Automated testing with mocked API calls |
| Packaging | Windows executable packager | Distribution |

## References & Guidelines

- **Architecture & Invariants:** [`AI/architecture.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/architecture.md)
- **UI & Design Tokens:** [`AI/ui-context.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ui-context.md) (referencing [Beautiful UI](https://github.com/Kainiko943/beautiful-ui))
- **Code Standards:** [`AI/code-standards.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/code-standards.md) (referencing [Ponytail](https://github.com/DietrichGebert/ponytail))
- **Workflow & Git Policy:** [`AI/ai-workflow-rules.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ai-workflow-rules.md)
- **Progress Tracking:** [`AI/progress-tracker.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/progress-tracker.md)

## Success Criteria

1. Desktop app launches reliably in pywebview with light-themed compact layout.
2. Server list displays icon, name, ID, owner status, and inferred category correctly.
3. Search (name/ID), sorting, and category filters function concurrently with persistent selection state.
4. Owned servers are strictly protected from selection and leave operations.
5. JSON/CSV exports produce valid data free of sensitive credentials.
6. Local preferences safely persist across application restarts.
7. Cleanup flow requires explicit confirmation, preserves server membership on preview/cancel, and reports verified results.
8. All automated tests pass using mocked data.