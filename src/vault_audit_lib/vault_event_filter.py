"""Event filter utilities.

Provides `VaultEventFilter` which tests whether a log entry matches a
specified key/value condition. Keys support dotted lookup (e.g.
`request.id`). The filter accepts a literal value, a callable, or a
compiled regex as the match criterion.
"""
from __future__ import annotations

import re
from typing import Any, Optional


class VaultEventFilter:
    """Filter events by key -> value match.

    Parameters
    - `key`: dotted key path to lookup in the event dict (e.g. "request.id").
    - `value`: match criterion. If callable, it will be called with the
       extracted value and should return truthy/falsey. If a `re.Pattern`,
       the pattern will be searched against the stringified value. Otherwise
       simple equality is used.
    """

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def _lookup(self, entry: Any) -> Optional[Any]:
        """Lookup dotted key in `entry` if it's a dict, else return None."""
        if not isinstance(entry, dict):
            return None
        cur: Any = entry
        for part in self.key.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    def _match_single(self, entry: Any) -> bool:
        """Match a single event entry (not a transaction)."""
        found = self._lookup(entry)
        # Callable matcher
        if callable(self.value):
            try:
                return bool(self.value(found))
            except Exception:
                return False

        # Regex matcher
        if isinstance(self.value, re.Pattern):
            if found is None:
                return False
            try:
                return self.value.search(str(found)) is not None
            except Exception:
                return False

        # Default equality
        return found == self.value

    def match(self, entry: Any) -> bool:
        """Return True if `entry` matches the configured key/value.

        Supports transactions represented as `(request_id, entries_iterable)`;
        in that case the method returns True if any event in the transaction
        matches the configured criterion.
        """
        # Detect transaction-like inputs and return True if any contained
        # event matches. Supported forms:
        # - (request_id, entries_iterable)
        # - sequence-of-events: [event1, event2, ...]
        if isinstance(entry, (list, tuple)):
            # (request_id, entries)
            if (
                len(entry) >= 2
                and isinstance(entry[0], str)
                and hasattr(entry[1], "__iter__")
                and not isinstance(entry[1], (str, bytes))
            ):
                entries_iter = entry[1]
            else:
                # treat the whole sequence as events
                entries_iter = entry

            # If entries_iter is a string/bytes, treat as single entry
            if isinstance(entries_iter, (str, bytes)):
                return self._match_single(entries_iter)

            for ev in entries_iter:
                if self._match_single(ev):
                    return True
            return False

        return self._match_single(entry)


__all__ = ["VaultEventFilter"]
