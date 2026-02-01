"""Reader for Vault audit `.private_log` files.

This module provides `VaultLogReader` which reads an audit log file
and yields one entry at a time. If a line is valid JSON, it yields
the parsed object (dict/list); otherwise it yields the raw line string.
The reader accepts file paths or file-like objects and transparently
handles gzip-compressed files when the filename ends with `.gz`.
"""
from __future__ import annotations

import gzip
import io
import json
from typing import IO, Any, Generator, Union


class VaultLogReader:
    """Read entries from a `.private_log` file.

    Usage:
      reader = VaultLogReader(path)
      for entry in reader:
          # entry is dict (if JSON) or str
    """

    def __init__(self, file: Union[str, IO]):
        self.file = file

    def __iter__(self) -> Generator[Any, None, None]:
        yield from self.read()

    def read(self) -> Generator[Any, None, None]:
        """Yield entries from the underlying file.

        Each non-empty line is attempted to be parsed as JSON. If parsing
        succeeds the resulting Python object is yielded; otherwise the raw
        string line is yielded.
        """
        file_obj: IO

        # Accept file-like objects directly
        if hasattr(self.file, "read"):
            file_obj = self.file  # type: ignore[assignment]
            close_after = False
        else:
            path = str(self.file)
            close_after = True
            if path.endswith(".gz"):
                file_obj = io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8")
            else:
                file_obj = open(path, "r", encoding="utf-8")

        try:
            for raw in file_obj:
                line = raw.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    yield line
        finally:
            if close_after:
                try:
                    file_obj.close()
                except Exception:
                    pass


__all__ = ["VaultLogReader"]
