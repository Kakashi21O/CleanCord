"""Application entry point and pywebview desktop shell lifecycle."""
import sys
import time
from pathlib import Path
from typing import Optional

import webview
from backend.bridge import DesktopBridge

APP_TITLE = "CleanCord"
DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 700
MIN_WIDTH = 800
MIN_HEIGHT = 600
MUTEX_NAME = "CleanCord_SingleInstance_Mutex"
CLICK_DEBOUNCE_SECONDS = 0.8
_mutex_handle = None


def get_base_path() -> Path:
    """Resolve base directory whether running from source or PyInstaller bundle."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_frontend_index_path() -> Path:
    """Resolve absolute path to frontend index.html."""
    return get_base_path() / "frontend" / "index.html"


def get_app_icon_path() -> Optional[Path]:
    """Resolve path to native CleanCord application icon."""
    icon_path = get_base_path() / "assets" / "cleancord.ico"
    return icon_path if icon_path.is_file() else None


def focus_existing_window() -> bool:
    """Bring the existing application window to front on Windows."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, APP_TITLE)
        if hwnd:
            # SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return True
    except Exception:
        pass
    return False


def is_ctrl_held() -> bool:
    """Check if Ctrl key is currently pressed."""
    if sys.platform == "win32":
        try:
            import ctypes
            # VK_CONTROL = 0x11
            return bool(ctypes.windll.user32.GetKeyState(0x11) & 0x8000)
        except Exception:
            pass
    return "--new-tab" in sys.argv or "-n" in sys.argv


def check_and_update_debounce() -> bool:
    """Return True if enough time elapsed since last click/launch attempt."""
    lock_file = Path(get_base_path()) / ".instance_click"
    now = time.time()
    try:
        if lock_file.is_file():
            last = float(lock_file.read_text(encoding="utf-8").strip())
            if now - last < CLICK_DEBOUNCE_SECONDS:
                return False
        lock_file.write_text(str(now), encoding="utf-8")
    except Exception:
        pass
    return True


def acquire_single_instance_lock() -> bool:
    """Acquire single-instance mutex. Returns True if first instance, False if already running."""
    global _mutex_handle
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        # CreateMutexW(lpMutexAttributes, bInitialOwner, lpName)
        _mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
        # ERROR_ALREADY_EXISTS = 183
        if ctypes.windll.kernel32.GetLastError() == 183:
            return False
        return True
    except Exception:
        return True


def apply_native_titlebar_theme(window: webview.Window) -> None:
    """Set native Windows title bar background to pure white and caption to dark."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = getattr(window, "native", None)
        if hwnd and hasattr(hwnd, "Handle"):
            hwnd_val = hwnd.Handle.ToInt32()
        else:
            hwnd_val = ctypes.windll.user32.FindWindowW(None, APP_TITLE)

        if hwnd_val:
            dwm = ctypes.windll.dwmapi
            set_attr = dwm.DwmSetWindowAttribute
            set_attr.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]

            # DWMWA_USE_IMMERSIVE_DARK_MODE (20): 0 for light title bar
            set_attr(hwnd_val, 20, ctypes.byref(ctypes.c_int(0)), 4)
            # DWMWA_CAPTION_COLOR (35): 0x00FFFFFF (pure white COLORREF in BGR: 0x00FFFFFF)
            set_attr(hwnd_val, 35, ctypes.byref(ctypes.c_int(0x00FFFFFF)), 4)
            # DWMWA_TEXT_COLOR (36): 0x00202020 (dark text COLORREF: ~#202020)
            set_attr(hwnd_val, 36, ctypes.byref(ctypes.c_int(0x00202020)), 4)
    except Exception:
        pass


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
        background_color="#FFFFFF",
    )
    window.events.shown += lambda: apply_native_titlebar_theme(window)
    return window


def main() -> None:
    """Launch desktop window with single-instance lock and focus handling."""
    # Check if user wants a new tab / window with Ctrl held
    ctrl_held = is_ctrl_held()

    if not ctrl_held:
        # Ignore accidental double/multi clicks
        if not check_and_update_debounce():
            focus_existing_window()
            return

        # Single instance check
        if not acquire_single_instance_lock():
            focus_existing_window()
            return

    bridge = DesktopBridge()
    create_window(bridge)
    icon_path = get_app_icon_path()
    icon_arg = str(icon_path) if icon_path else None
    webview.start(debug=False, icon=icon_arg)


if __name__ == "__main__":
    main()
