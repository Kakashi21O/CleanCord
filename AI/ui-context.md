# UI Context

## Design Direction

Server Prune features a clean, minimal, light-themed Windows desktop interface optimized for high-density server management.

- **Design Reference:** Follow [Beautiful UI](https://github.com/Kainiko943/beautiful-ui) for component structure, accessibility, visual hierarchy, and interaction feedback.
- **Theme Constraint:** Light theme only. No dark mode unless explicitly requested.
- **Dependencies:** Lightweight native HTML/CSS with custom properties; no heavy UI component libraries.

## Design Tokens

### Colors (CSS Custom Properties)
All components must use these variables:

| Role | Variable | Value | Notes |
|---|---|---|---|
| Background Base | `--bg-base` | `#F5F7FA` | Desktop window background |
| Surface | `--bg-surface` | `#FFFFFF` | Main panels, cards, inputs |
| Subtle Surface | `--bg-subtle` | `#F0F2F5` | Secondary panels, chips |
| Hover Surface | `--bg-hover` | `#F3F6FA` | Interactive hover state |
| Selected Background | `--selection-bg` | `#EEF0FF` | Selected row highlight |
| Primary Text | `--text-primary` | `#202431` | High-contrast main copy |
| Secondary Text | `--text-secondary` | `#636B7A` | Labels, metadata |
| Muted Text | `--text-muted` | `#858D9B` | Placeholders, inactive info |
| Primary Accent | `--accent-primary` | `#5865F2` | Buttons, checkboxes, active filters |
| Accent Hover | `--accent-hover` | `#4752C4` | Primary hover state |
| Default Border | `--border-default` | `#E1E5EB` | Standard component border |
| Strong Border | `--border-strong` | `#C8CFDA` | Focused/emphasized borders |
| Error / Destructive | `--state-error` | `#D92D3A` | Cleanup button, error text |
| Error Background | `--state-error-bg` | `#FFF0F0` | Error banners, warnings |
| Success | `--state-success` | `#20865A` | Success confirmation |
| Success Background | `--state-success-bg` | `#EAF8F0` | Success banners |
| Warning | `--state-warning` | `#A86812` | Cautions |
| Warning Background | `--state-warning-bg` | `#FFF5E5` | Warning banners |

### Typography
Use native Windows system fonts:
- `--font-sans`: System sans-serif UI stack (`Segoe UI`, system-ui, sans-serif).
- `--font-mono`: System monospace stack (`Consolas`, monospace) for IDs.
- **Scale:** Title: 22–26px | Section Headings: 15–17px | Server Name: 14px | Body: 13–14px | Badges/Labels: 11–12px.

### Spacing & Sizing
- Spacing tokens: `--space-1` (4px), `--space-2` (8px), `--space-3` (12px), `--space-4` (16px), `--space-5` (20px), `--space-6` (24px), `--space-8` (32px).
- Border radius: Small badges (5–6px), Inputs/Buttons (7px), Rows/Panels (9px), Modals (12px), Server Icons (8px or circular).

## Layout & Components

### Application Window Layout
1. **Header:** App title and primary status / actions.
2. **Filter & Search Bar:** Instant search (name/ID), alphabetical sort toggle, category filter chips (All, Gaming, Anime, Development, Crypto / DeFi, NFT, Trading, Other).
3. **Selection Toolbar:** Counter ("X servers selected"), Select All, Deselect All.
4. **Server List Container:** Vertically scrollable, compact list with medium row spacing (`--space-3`).
5. **Footer / Action Bar:** Export buttons (JSON / CSV), cleanup preview button (red accent).

### Server Row Structure
Compact collapsed row layout:
- **Left:** Server icon (or neutral placeholder image/fallback).
- **Center:** Server name (primary text) with server ID (monospace, secondary text) and badge tags (owner status, category).
- **Right:** Checkbox for selection to leave.
- **Expandable Details:** Optional small expandable drawer for secondary info. Clicking row expands details; row expansion must **not** toggle selection checkbox.

### Interaction & State Rules

- **Selection Rule:** Checked = selected to leave.
- **Owner Safeguard:** Servers owned by user must display an Owner badge and have disabled, uncheckable checkboxes.
- **Interactive States:** All buttons, chips, rows, and inputs must implement default, hover, focus-visible (accessibility outline), selected, and disabled states.
- **Feedback & Confirmation:**
  - Search/filter updates must be instantaneous and show an empty state if no matches exist.
  - Loading state: Display indicator while fetching servers; never show mock data as real data.
  - Cleanup action: Requires explicit confirmation modal showing total count of servers to leave. Show progress and confirmed real-time results during execution.