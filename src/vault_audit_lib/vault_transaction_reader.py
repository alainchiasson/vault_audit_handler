"""Buffered reader that groups Vault log entries into transactions.

`VaultTransactionReader` wraps a `VaultLogReader` (the
package exposes `VaultLogReader` from `vault_log_reader`) and yields
transactions. A transaction is the set of all log events that share the
same `request.id`.

The reader collects entries keyed by `request.id` and yields a transaction
when a configurable `is_final` predicate signals completion for that
request, or when the source hits EOF (remaining buffered transactions are
yielded).
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Tuple

from .vault_log_reader import VaultLogReader


def _extract_request_id(entry: Any) -> Optional[str]:
    if not isinstance(entry, dict):
        return None
    # Get entry["request"]["id"] Or None
    req = entry.get("request")
    if isinstance(req, dict):
        rid = req.get("id")
        if isinstance(rid, str):
            return rid
    return None


def _default_is_final(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    entry_type = entry.get("type")
    if isinstance(entry_type, str) and entry_type.lower() == "response":
        return True
    return False


class VaultTransactionReader:
    """Group Vault log entries into transactions by `request.id`.

    Parameters
    - source: path string, file-like object, or an iterable yielding entries (e.g., `VaultLogReader`).
    - is_final: optional callable `entry -> bool` to mark when an entry completes a transaction.
    - close_on_eof: if True, yield any buffered transactions at EOF.

    Yields tuples `(request_id, entries_list)`.
    """

    def __init__(
        self,
        source: Iterable[Any],
        is_final: Callable[[Any], bool] = _default_is_final,
        close_on_eof: bool = True,
    ) -> None:
        if isinstance(source, (str, bytes)):
            # allow passing a file path
            self.reader = VaultLogReader(str(source))
        else:
            # assume iterable/generator of entries
            self.reader = source  # type: ignore[assignment]
        self.is_final = is_final
        self.close_on_eof = close_on_eof

    def __iter__(self) -> Generator[Tuple[str, List[Any]], None, None]:
        yield from self.read()

    def read(self) -> Generator[Tuple[str, List[Any]], None, None]:
        buffers: Dict[str, List[Any]] = defaultdict(list)
        ready: deque = deque()

        for entry in self.reader:
            rid = _extract_request_id(entry)
            if rid is None:
                # ignore or treat as a transactionless event; skip
                continue
            buffers[rid].append(entry)
            if self.is_final(entry):
                ready.append(rid)

            while ready:
                rid_to_yield = ready.popleft()
                entries = buffers.pop(rid_to_yield, [])
                if entries:
                    yield rid_to_yield, entries

        if self.close_on_eof:
            # yield any remaining buffered transactions
            for rid, entries in list(buffers.items()):
                if entries:
                    yield rid, entries


__all__ = ["VaultTransactionReader"]
