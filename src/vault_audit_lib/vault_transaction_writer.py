"""Write transactions as log entries in time order.

This module provides `VaultTransactionWriter` which accepts transactions
(`(request_id, entries)`) and writes their constituent log entries to a
Vault audit log file ensuring global ordering by the `time` field.
"""
from __future__ import annotations

import heapq
import itertools
from typing import IO, Any, Iterable, Tuple, Union

from .vault_log_writer import VaultLogWriter


def _extract_time(entry: Any, time_key: str) -> str:
    if isinstance(entry, dict):
        val = entry.get(time_key)
        if val is None:
            return ""
        return str(val)
    # Non-dict entries: treat as earliest
    return ""


class VaultTransactionWriter:
    """Write transactions to a Vault audit log file in time order.

    Usage:
        writer = VaultTransactionWriter(path)
        writer.write_transaction(request_id, entries)
        writer.write_transactions(iter_of_transactions)
    """

    def __init__(self, file: Union[str, IO], mode: str = "a") -> None:
        self._writer = VaultLogWriter(file, mode=mode)

    def write_transaction(
        self, request_id: str, entries: Iterable[Any], time_key: str = "time"
    ) -> None:
        """Write a single transaction's entries in time order."""
        entries_list = list(entries)
        entries_list.sort(key=lambda e: _extract_time(e, time_key))
        for e in entries_list:
            self._writer.write(e)

    def write_transactions(
        self, transactions: Iterable[Tuple[str, Iterable[Any]]], time_key: str = "time"
    ) -> None:
        """Write multiple transactions merged by their entry times.

        `transactions` is an iterable yielding `(request_id, entries_iterable)`.
        Entries within each transaction may be unsorted; this method will
        sort per-transaction entries and then perform an efficient k-way
        merge to produce a globally time-ordered stream of entries.
        """

        # Prepare iterators of sorted entries for each transaction
        iterators = []
        for _rid, entries in transactions:
            lst = list(entries)
            lst.sort(key=lambda e: _extract_time(e, time_key))
            if lst:
                iterators.append(iter(lst))

        # Build initial heap
        heap = []
        counter = itertools.count()
        for it in iterators:
            try:
                e = next(it)
            except StopIteration:
                continue
            t = _extract_time(e, time_key)
            heapq.heappush(heap, (t, next(counter), e, it))

        while heap:
            t, _c, e, it = heapq.heappop(heap)
            self._writer.write(e)
            try:
                nxt = next(it)
            except StopIteration:
                continue
            heapq.heappush(heap, (_extract_time(nxt, time_key), next(counter), nxt, it))

    def flush(self) -> None:
        self._writer.flush()

    def close(self) -> None:
        try:
            self._writer.close()
        except Exception:
            pass

    def __enter__(self) -> "VaultTransactionWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.flush()
        self.close()


__all__ = ["VaultTransactionWriter"]
