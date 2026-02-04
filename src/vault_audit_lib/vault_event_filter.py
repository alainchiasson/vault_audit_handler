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

    def match(self, entry: Any) -> bool:
        """Return True if `entry` matches the configured key/value.

        Matching rules:
        - If `value` is callable: return `bool(value(found))`.
        - If `value` is a compiled `re.Pattern`: return whether it matches
          the stringified found value.
        - Otherwise: return equality comparison `found == value`.
        """
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


__all__ = ["VaultEventFilter"]
