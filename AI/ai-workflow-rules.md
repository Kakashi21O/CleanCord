# AI Workflow Rules

## Principles

Develop Server Prune incrementally using a spec-driven workflow. The documents in `AI/` are the authoritative source of truth:
- [`AI/project-overview.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/project-overview.md) — Scope, goals, and feature requirements.
- [`AI/architecture.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/architecture.md) — System boundaries, data models, and architectural invariants.
- [`AI/code-standards.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/code-standards.md) — Coding conventions, safety, and testing rules.
- [`AI/ui-context.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ui-context.md) — Light theme design tokens, layout, and component states.
- [`AI/progress-tracker.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/progress-tracker.md) — Work status and completed/pending units.

**Engineering References:**
- **Code implementation & testing:** [Ponytail](https://github.com/DietrichGebert/ponytail) (minimal correct solutions, standard libraries, no speculative bloat).
- **UI/UX & accessibility:** [Beautiful UI](https://github.com/Kainiko943/beautiful-ui) (visual design, contrast, and interactive feedback).

## Scoping & Task Execution

- Implement one small, testable unit at a time.
- Split work if a task mixes unrelated concerns (e.g., UI redesign + backend auth).
- If requirements are unclear, check the `AI/` docs first. Log unresolved decisions in `progress-tracker.md` or prompt the user for direction before making assumptions.
- Never invent product features or bypass platform restrictions.

## Git Workflow & Policies

`master` is strictly for stable, tested code.

1. **Inspect status:** Run `git status` / `git diff` before and after modifying files.
2. **Branching:** Create feature branches sequentially from latest `master`.
   - `1-foundation`
   - `2-server-list`
   - `3-local-utilities`
   - `4-discord-integration`
   - `5-cleanup-workflow`
   - `6-release`
3. **Commit naming:** Numbered commits matching branch & unit: `<branch>.<unit>-<short-description>`.
   - Examples: `1.1-project-setup`, `1.2-desktop-window`, `1.3-static-ui`.
4. **Testing & Verification:** Run tests after every unit. Automated tests must use mock data and must **never** execute real Discord leave actions.
5. **No direct pushes / unapproved merges:**
   - Never commit directly to `master`.
   - Never merge feature branches into `master` without explicit user sign-off.
   - Never force-push or discard user changes without permission.

## Documentation & Progress Sync

- Update `AI/progress-tracker.md` after every meaningful implementation unit.
- If architectural boundaries, storage formats, or API policies change, update `architecture.md` immediately.

## Unit & Branch Completion Checklist

**For each unit:**
1. Code satisfies unit specifications without unintended scope changes.
2. Relevant unit/integration tests executed and passed.
3. No credentials exposed in files, logs, or commits.
4. `AI/progress-tracker.md` updated.
5. Numbered commit created on the feature branch.

**For each feature branch:**
1. All planned units are completed and verified.
2. Branch-level regression check and test suite passes.
3. Report summary of changes, commit IDs, and known limitations to the user.
4. Wait for explicit user confirmation before merging to `master`.