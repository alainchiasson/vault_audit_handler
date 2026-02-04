#!/usr/bin/env python3
"""Print to console all events where `error is present`."""
from __future__ import annotations

import argparse
import json

from vault_audit_lib import VaultEventFilter, VaultLogReader


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print all events with errors to stdout"
    )
    parser.add_argument("path", help="Path to the audit log file (.private_log or .gz)")
    args = parser.parse_args()

    reader = VaultLogReader(args.path)
    filt = VaultEventFilter("error", lambda v: v is not None)

    for entry in reader:
        if filt.match(entry):
            # Print JSON for dicts, or raw line otherwise
            if isinstance(entry, dict):
                print(json.dumps(entry, ensure_ascii=False))
            else:
                print(entry)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
