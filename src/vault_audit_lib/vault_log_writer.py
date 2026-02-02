"""Writer for Vault audit log files.

Provides `VaultLogWriter` to append entries to a Vault audit log file.
Entries are written as JSON lines. Accepts a path (text or .gz) or a
file-like object opened for text writing.
"""
from __future__ import annotations

import gzip
import json
from typing import IO, Any, Iterable, Optional, Union


class VaultLogWriter:
    """Append entries to a Vault audit log file.

    Example:
        with VaultLogWriter("/var/log/.private_log") as w:
            w.write({"request": {"id": "1"}, "msg": "start"})
    """

    def __init__(self, file: Union[str, IO], mode: str = "a") -> None:
        self._close_after = False
        if hasattr(file, "write"):
            self._file = file  # type: ignore[assignment]
        else:
            path = str(file)
            self._close_after = True
            if path.endswith(".gz"):
                # gzip text append
                self._file = gzip.open(path, mode + "t", encoding="utf-8")
            else:
                self._file = open(path, mode, encoding="utf-8")

    def write(self, entry: Any) -> None:
        """Write a single entry as a JSON line.

        If `entry` is a string it is written verbatim (with newline).
        Otherwise it is serialized with `json.dumps`.
        """
        if isinstance(entry, str):
            line = entry
        else:
            line = json.dumps(entry, default=str)
        if not line.endswith("\n"):
            line = line + "\n"
        self._file.write(line)

    def writelines(self, entries: Iterable[Any]) -> None:
        for e in entries:
            self.write(e)

    def flush(self) -> None:
        try:
            self._file.flush()
        except Exception:
            pass

    def close(self) -> None:
        if self._close_after:
            try:
                self._file.close()
            except Exception:
                pass

    def __enter__(self) -> "VaultLogWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:
        self.flush()
        self.close()
        return None


__all__ = ["VaultLogWriter"]
