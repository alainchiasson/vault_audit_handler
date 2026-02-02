#!/usr/bin/env python3
"""Simple example: read a Vault audit log and print each entry to stdout."""
from __future__ import annotations

import argparse
import json

from vault_audit_lib import VaultLogReader


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a Vault audit log and print entries"
    )
    parser.add_argument(
        "path", help="Path to the audit log file (.private_log or .private_log.gz)"
    )
    args = parser.parse_args()

    reader = VaultLogReader(args.path)
    for entry in reader:
        if isinstance(entry, str):
            print(entry)
        else:
            print(json.dumps(entry, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
