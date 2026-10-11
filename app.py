"""Application entry point and pywebview desktop shell lifecycle."""
import sys
from pathlib import Path
from typing import Optional

import webview
from backend.bridge import DesktopBridge

APP_TITLE = "CleanCord"
DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 700
MIN_WIDTH = 800
MIN_HEIGHT = 600


def get_frontend_index_path() -> Path:
    """Resolve absolute path to frontend index.html."""
    return Path(__file__).resolve().parent / "frontend" / "index.html"


def create_window(bridge: Optional[DesktopBridge] = None) -> webview.Window:
    """Create pywebview window with explicit bridge API."""
    index_file = get_frontend_index_path()
    if not index_file.is_file():
        raise FileNotFoundError(f"Frontend entry point not found at {index_file}")

    api = bridge or DesktopBridge()
    window = webview.create_window(
        title=APP_TITLE,
        url=str(index_file.as_uri()),
        js_api=api,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
    )
    return window


def main() -> None:
    """Launch desktop window."""
    bridge = DesktopBridge()
    create_window(bridge)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
