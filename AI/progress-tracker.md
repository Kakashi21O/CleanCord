# Progress Tracker

## Current Status

- **Project:** Server Prune
- **Phase:** Foundation
- **Current branch:** `1-foundation`
- **Current commit:** In progress (`1.1-project-setup`)
- **Next unit:** `1.2-desktop-window`
- **Merge status:** No feature branch merged yet

> Branch and commit details must be updated from actual Git state. Never assume a branch, commit, or merge exists without verification.

## Branch & Implementation Plan

### Branch: `1-foundation`

| Commit | Unit | Status |
|---|---|---|
| `1.1-project-setup` | Establish minimal directory structure, dependencies, and git baseline | Completed |
| `1.2-desktop-window` | Launch pywebview desktop shell and bridge lifecycle | Pending |
| `1.3-static-ui` | Implement light-themed UI shell with mock server data | Pending |

### Branch Tracking

| Branch | Development Status | User Approval | Merge to `master` |
|---|---|---|---|
| `1-foundation` | Not started | Pending | Not merged |
| `2-server-list` | Not started | Pending | Not merged |
| `3-local-utilities` | Not started | Pending | Not merged |
| `4-discord-integration` | Not started | Pending | Not merged |
| `5-cleanup-workflow` | Not started | Pending | Not merged |
| `6-release` | Not started | Pending | Not merged |

## Open Decisions & Questions

1. **Authentication:** Which supported authentication mechanism can provide the required server-list and server-leave capabilities without unauthorized user-token automation?
2. **Packaging:** Which Windows executable packager best fits the desktop app (e.g., PyInstaller)?
3. **Storage schema:** Should server whitelist persist in `preferences.json` or as a standalone `whitelist.json`?

*(Architecture specifications are detailed in [`AI/architecture.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/architecture.md) and workflow rules in [`AI/ai-workflow-rules.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ai-workflow-rules.md).)*

## Verification Checklist

### For Each Unit
- [ ] Requirements implemented to spec without extra scope.
- [ ] Automated tests executed with mocked data and passed.
- [ ] Error handling, security boundaries, and edge cases verified.
- [ ] No secrets exposed in files, commits, or exports.
- [ ] Progress tracker and relevant `AI/` docs updated.
- [ ] Numbered commit created (`<branch>.<unit>-<name>`).

### For Each Feature Branch
- [ ] All units in the branch completed and tested.
- [ ] Full regression check passed.
- [ ] Results and limitations reported to user.
- [ ] Explicit user approval received before merging into `master`.
- [ ] Verified `master` after merge.