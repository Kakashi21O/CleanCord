# CleanCord — Discord Server Cleanup

A lightweight Windows desktop application for viewing, searching, and leaving Discord servers through a clean, minimal interface.

[![Download CleanCord](https://img.shields.io/badge/Download-CleanCord.exe%20(v1.0.0)-blue?style=for-the-badge&logo=windows)](https://github.com/Kakashi21O/CleanCord/releases/latest/download/CleanCord.exe)

## 📥 Download & Install (For Users)

Anyone can download and run CleanCord on Windows without installing Python:

1. Go to the [**CleanCord v1.0.0 Release**](https://github.com/Kakashi21O/CleanCord/releases/tag/v1.0.0) or click [**Direct Download (CleanCord.exe)**](https://github.com/Kakashi21O/CleanCord/releases/latest/download/CleanCord.exe).
2. Download `CleanCord.exe`.
3. Double-click `CleanCord.exe` to run the app immediately (no installation or setup required).

---

## Features

- 🔍 **Search & filter** servers by name, ID, or category
- 📂 **Category chips** — Gaming, Anime, Development, Crypto/DeFi, NFT, Trading, Other
- ☑️ **Select / deselect all** eligible servers at once
- 🛡️ **Owner protection** — servers you own are never eligible for cleanup
- 👁️ **Preview cleanup** — see exactly which servers will be left before confirming
- 📤 **Export** server list to JSON or CSV
- 💾 **Persistent preferences** — window size and sort order saved locally
- 🖥️ **Native desktop window** with a real Windows icon (`cleancord.ico`)

---

## Requirements

- **Python 3.8+**
- **Windows** (pywebview uses EdgeChromium / WinForms on Windows)

Install dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently contains:

```
pywebview>=5.0.0
```

---

## How to Run

```bash
python app.py
```

The app opens as a native desktop window titled **CleanCord**.  
By default it starts in **Demo Mode** with sample server data so you can explore without a token.

---

## How to Connect Discord (Live Mode)

> [!CAUTION]
> Using a self-bot token violates Discord's Terms of Service. Use this tool responsibly and only on your own account. Never share your token.

To use CleanCord with your real Discord servers:

### 1. Get your Discord user token

1. Open Discord in your **browser** (discord.com/app).
2. Press **F12** to open DevTools → go to the **Network** tab.
3. Refresh the page or click any channel.
4. Filter requests by `XHR` or search for `api`.
5. Click any Discord API request → **Headers** tab.
6. Find the `Authorization` header — the value is your token.

> [!WARNING]
> Do **not** copy tokens starting with `Bot ` — those are bot tokens. Your user token has no prefix.

### 2. Connect in the app

1. Click the **Connect Discord** button (top-right).
2. Paste your token into the input field.
3. Click **Connect**.

CleanCord validates the token against the Discord API, fetches your full server list (all pages), and switches to **Live Mode**.  
Your token is **never written to disk** — it is held only in memory for the session.

---

## How Cleanup Works

1. **Browse** your server list — search, filter by category, or scroll.
2. **Select** the servers you want to leave (owned servers are automatically excluded).
3. Click **Preview Cleanup** — a modal shows exactly which servers will be left and which are protected.
4. Click **Leave Servers** to confirm.
   - In **Demo Mode**: simulates leaving with no real API calls.
   - In **Live Mode**: calls `DELETE /users/@me/guilds/{id}` for each eligible server.
5. Left servers are removed from the list immediately.

---

## Project Structure

```
CleanCord/
├── app.py                        # Entry point — pywebview window
├── requirements.txt
├── assets/
│   └── cleancord.ico             # Windows application icon
├── backend/
│   ├── bridge.py                 # JS ↔ Python API bridge (DesktopBridge)
│   ├── cleanup/
│   │   └── service.py            # Preview & execute cleanup logic
│   ├── exports/
│   │   └── exporter.py           # JSON / CSV export
│   ├── integrations/
│   │   └── client.py             # Discord API client (urllib only)
│   ├── servers/
│   │   ├── model.py              # Server dataclass
│   │   ├── categorizer.py        # Keyword-based category inference
│   │   ├── normalizer.py         # Raw API dict → Server
│   │   └── service.py            # Filter, sort, select helpers
│   └── storage/
│       └── manager.py            # Preferences & whitelist (~/.cleancord/)
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── tests/
    ├── test_setup.py
    ├── test_window.py
    ├── test_ui.py
    ├── test_servers.py
    ├── test_export.py
    ├── test_storage.py
    ├── test_api_client.py
    └── test_cleanup.py
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests use mock data — no live network calls are made.

---

## Security Notes

- Your Discord token is **never saved to disk**.
- Owned servers are **always protected** from cleanup — enforced at both preview and execution time.
- Exports contain only: server name, ID, owner flag, category, icon URL — no credentials.
- The whitelist (`~/.cleancord/whitelist.json`) lets you permanently protect specific servers.

---

## Status

Active development — core features complete.

| Branch | Feature | Status |
|---|---|---|
| `1-foundation` | Desktop shell, pywebview, UI scaffold | ✅ Merged |
| `2-server-list` | Server model, categorizer, filter/sort | ✅ Merged |
| `3-local-utilities` | JSON/CSV export, preferences storage | ✅ Merged |
| `4-discord-integration` | Discord API client, token connect, live mode | ✅ Merged |
| `5-cleanup-workflow` | Preview modal, leave execution, owner guard | ✅ Merged |

---

## License

Not yet decided.