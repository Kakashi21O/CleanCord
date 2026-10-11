# Code Standards

## Core Engineering Principles

- **Minimal & maintainable:** Follow [Ponytail](https://github.com/DietrichGebert/ponytail) guidance — understand existing code first, reuse working solutions, fix root causes, and write the smallest correct change.
- **Accessible UI:** Follow [Beautiful UI](https://github.com/Kainiko943/beautiful-ui) for design tokens, accessibility, and interaction states. Detailed UI specs reside in [`AI/ui-context.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ui-context.md).
- **Safety over brevity:** Never sacrifice security, input validation, owner protection, or error handling to reduce line count.

## Python Standards

- **Style:** PEP 8 compliance; descriptive naming; type hints on public functions and core data structures.
- **Dependencies:** Prefer Python standard library (`pathlib`, `json`, `csv`, `unittest`). Introduce external dependencies only with explicit justification.
- **Error Handling:** Avoid broad `except:` catches. Validate external inputs. Never swallow exceptions or falsely report failed operations as successful.
- **Architecture separation:** Keep API client, pywebview bridge, business logic, storage, and export logic strictly decoupled (see [`AI/architecture.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/architecture.md)).

## Frontend Standards (HTML/CSS/JS)

- **Vanilla stack:** Clean semantic HTML5, modern CSS3, and vanilla ES6+ JavaScript. No unnecessary frontend frameworks or heavyweight component libraries.
- **Token consistency:** All styling must derive from CSS variables defined in [`AI/ui-context.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ui-context.md). No inline styles or ad-hoc hex values.
- **State handling:** Every interactive component must handle default, hover, active, focus, disabled, loading, and error states.
- **Accessibility:** Keyboard navigable, visible focus outlines, and appropriate ARIA attributes/labels.

## pywebview Desktop Bridge

- Expose only explicitly required backend methods.
- Validate all bridge arguments on the Python backend; treat frontend input as untrusted.
- Never expose arbitrary shell, filesystem, or dynamic code execution capabilities.
- Destructive actions (server leave) must be gated by backend safety checks, never relying solely on frontend state.

## API & Data Security

- **Secrets:** Never hardcode credentials. Zero token exposure in frontend JavaScript, logs, exports, screenshots, or Git commits.
- **Minimal access:** Never query or store member counts, channel messages, or server timestamps.
- **Storage:** Server IDs must always be strings (avoid numeric truncation/overflow). Exports must be valid UTF-8 with proper CSV escaping and JSON formatting.

## Testing Standards

- Write focused tests for parsing, filtering, sorting, exports, owner protection, and error handling.
- Mock all network interactions — tests must never make real Discord API requests or execute actual leave operations.
- Verify tests pass locally before committing. Never claim unexecuted tests passed.

## Definition of Done

A task unit is complete only when:
1. Requirements are met without regression or scope creep.
2. Architecture and code standards are respected.
3. Relevant unit/integration tests pass with mocked data.
4. Error conditions and edge cases are handled safely.
5. Context documentation and [`AI/progress-tracker.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/progress-tracker.md) are updated.
6. Git commit adheres to [`AI/ai-workflow-rules.md`](file:///c:/Users/vijay/OneDrive/Documents/Git/CleanCord/AI/ai-workflow-rules.md).