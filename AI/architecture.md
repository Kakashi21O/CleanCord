# Architecture Context

## Stack

| Layer | Technology | Role |
|---|---|---|
| Desktop shell | pywebview | Windows desktop window container |
| Frontend | HTML, CSS, JavaScript | Web UI rendering and local interactions |
| Backend | Python 3 | Business logic, normalization, storage, exports |
| Desktop bridge | pywebview JS API | Exposes only explicit, strictly validated Python methods |
| Network | Python standard library | API communication (when configured) |
| Testing | unittest / pytest | Unit & integration tests with mocked API calls |
| Packaging | Windows executable packager | Distribution (e.g., PyInstaller) |

## System Boundaries

- `app.py` — Entry point & pywebview window lifecycle.
- `frontend/` — HTML templates, CSS styles, JavaScript, static assets.
- `backend/` — UI-independent application services:
  - `backend/servers/` — Server data normalization, local category inference, search/sort/selection helpers.
  - `backend/integrations/` — API integration and authentication boundaries.
  - `backend/cleanup/` — Cleanup preview, safety/eligibility verification, execution, and result reporting.
  - `backend/storage/` — Local JSON persistence for preferences and whitelist.
  - `backend/exports/` — JSON and CSV serialization.
- `tests/` — Automated tests with mocked network responses and isolated files.
- `AI/` — Specs, architecture, standards, UI context, workflow rules, and progress tracking.

Keep modular boundaries minimal; only introduce new subpackages when justified by complexity.

## Data Model & Specifications

### Server
Internal normalized representation:
- `id` (str): Server ID.
- `name` (str): Server display name.
- `icon_url` (str | null): Server icon URL or null if absent.
- `owner` (bool): True if current account owns the server.
- `category` (str): Locally inferred category (Gaming, Anime, Development, Crypto / DeFi, NFT, Trading, Other).

Do not fetch or store member counts, channel lists, messages, or timestamps.

### Selection State
- State is decoupled from the underlying server records.
- Checked = selected to leave.
- Filter/search changes preserve active selections.
- Bulk operations (Select/Deselect All) target eligible servers in the active filtered view.
- Owned servers are strictly ineligible (`owner == True` can never be selected).
- Eligibility must be re-verified immediately before executing any cleanup operation.

### Preferences & Whitelist Storage
- **Preferences:** Stored in local JSON (window geometry, sort choice, UI preferences). Missing or malformed configurations must fall back gracefully to defaults.
- **Whitelist:** Stored as a list of server IDs (strings). Whitelist settings must never contain credentials or override owner protection safeguards.

### Exports
- JSON and CSV output must include: `id`, `name`, `owner`, `category`, `icon_url`.
- Never serialize credentials, tokens, session IDs, or internal security fields.

## Authentication & Security Model

- **Authentication constraint:** User-token automation (as seen in legacy scripts) risks account termination. The authentication mechanism remains an explicit design decision that must be reviewed and approved before live operations are permitted.
- **Frontend isolation:** Tokens and credentials must never reach frontend JavaScript, logs, exports, or Git commits. All sensitive logic resides in Python backend services.
- **Bridge validation:** Treat all pywebview bridge parameters as untrusted. No arbitrary shell, filesystem, or Python execution APIs may be exposed.
- **Operation gates:** Live cleanup remains disabled until supported authentication is approved.

## System Invariants

1. **Frontend Isolation:** Zero access to secrets or raw account APIs from frontend code.
2. **Safe Defaults:** Startup only loads and displays data; never triggers cleanup actions automatically.
3. **Owner Protection:** `owner == True` servers are immutable and permanently ineligible for removal.
4. **Explicit Confirmation:** Any cleanup requires a preview dialog and explicit user confirmation.
5. **Minimal Data Access:** Only fetch required server fields; never request member counts or dates.
6. **Accurate Reporting:** Report success only when verified by backend/API response.
7. **Local Categorization:** Category inference runs strictly locally without external network requests.
8. **Test Isolation:** Automated tests must use mock data and never execute live network or leave actions.
9. **Credential Safety:** Storage and exports must never persist tokens or secrets.
10. **UI Responsiveness:** Async/background execution prevents pywebview UI freezes during long-running tasks.
11. **Approval-Controlled Merges:** No branch merges to `master` without explicit user sign-off.

## Data Flow

1. App launches -> pywebview loads frontend -> Backend loads local preferences.
2. Backend loads server records (mock data or approved integration) and normalizes into internal Server model.
3. Frontend renders compact server list.
4. Search, sorting, and category filters execute locally in frontend/bridge.
5. User selects servers -> UI displays count and preview summary.
6. User triggers cleanup -> Backend verifies eligibility -> Prompts explicit confirmation -> Executes approved operation -> Returns verified result summary.
7. Server list refreshes upon completion.

## Open Architectural Decisions

- Approved authentication strategy for Discord server management.
- Choice of Windows executable packaging tool (e.g., PyInstaller).
- Whitelist file schema (standalone file vs. integrated into preferences).

*(Track status and resolution in [`AI/progress-tracker.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/progress-tracker.md).)*