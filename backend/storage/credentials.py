"""Windows Credential Manager integration for CleanCord.

Securely stores, retrieves, and deletes sensitive credentials
using the native Windows Credential Manager (advapi32.dll),
ensuring secrets are never written to application settings, config files, or logs.
"""
import ctypes
from ctypes import POINTER, Structure, byref, c_void_p
from ctypes import wintypes
import sys
from typing import Optional

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


class CREDENTIAL(Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


PCREDENTIAL = POINTER(CREDENTIAL)


class WindowsCredentialStore:
    """Manages credentials via Windows Credential Manager API."""

    DEFAULT_TARGET_NAME = "CleanCord/DiscordToken"
    DEFAULT_USERNAME = "CleanCordUser"

    def __init__(self, target_name: str = DEFAULT_TARGET_NAME) -> None:
        self.target_name = target_name
        self.is_windows = sys.platform == "win32"
        if self.is_windows:
            self._advapi32 = ctypes.windll.advapi32
            self._advapi32.CredWriteW.argtypes = [PCREDENTIAL, wintypes.DWORD]
            self._advapi32.CredWriteW.restype = wintypes.BOOL

            self._advapi32.CredReadW.argtypes = [
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                POINTER(PCREDENTIAL),
            ]
            self._advapi32.CredReadW.restype = wintypes.BOOL

            self._advapi32.CredDeleteW.argtypes = [
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
            ]
            self._advapi32.CredDeleteW.restype = wintypes.BOOL

            self._advapi32.CredFree.argtypes = [c_void_p]
            self._advapi32.CredFree.restype = None

    def save_credential(self, secret: str, username: str = DEFAULT_USERNAME) -> bool:
        """Store secret in Windows Credential Manager.

        Never writes to configuration files or logs.
        """
        if not self.is_windows or not secret:
            return False

        try:
            secret_bytes = secret.encode("utf-8")
            blob_buf = (ctypes.c_byte * len(secret_bytes))(*secret_bytes)

            cred = CREDENTIAL()
            cred.Flags = 0
            cred.Type = CRED_TYPE_GENERIC
            cred.TargetName = self.target_name
            cred.Comment = "CleanCord Authorization Token"
            cred.CredentialBlobSize = len(secret_bytes)
            cred.CredentialBlob = ctypes.cast(blob_buf, POINTER(ctypes.c_byte))
            cred.Persist = CRED_PERSIST_LOCAL_MACHINE
            cred.AttributeCount = 0
            cred.Attributes = None
            cred.TargetAlias = None
            cred.UserName = username

            result = self._advapi32.CredWriteW(byref(cred), 0)
            return bool(result)
        except Exception:
            return False

    def get_credential(self) -> Optional[str]:
        """Retrieve stored secret from Windows Credential Manager.

        Returns None if not present or on failure.
        """
        if not self.is_windows:
            return None

        pcred = PCREDENTIAL()
        try:
            success = self._advapi32.CredReadW(
                self.target_name,
                CRED_TYPE_GENERIC,
                0,
                byref(pcred),
            )
            if success and pcred:
                try:
                    blob_ptr = pcred.contents.CredentialBlob
                    blob_size = pcred.contents.CredentialBlobSize
                    if blob_ptr and blob_size > 0:
                        raw_bytes = ctypes.string_at(blob_ptr, blob_size)
                        return raw_bytes.decode("utf-8")
                finally:
                    self._advapi32.CredFree(pcred)
        except Exception:
            pass
        return None

    def delete_credential(self) -> bool:
        """Delete stored credential from Windows Credential Manager."""
        if not self.is_windows:
            return False

        try:
            result = self._advapi32.CredDeleteW(
                self.target_name,
                CRED_TYPE_GENERIC,
                0,
            )
            return bool(result)
        except Exception:
            return False
