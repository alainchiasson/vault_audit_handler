#!/usr/bin/env python3
"""Read a Vault audit log and write entries to a new file.

Usage:
  python examples/read_and_write_vault_log.py input.private_log output.private_log
"""
from __future__ import annotations

import argparse

from vault_audit_lib import VaultLogReader, VaultLogWriter


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a Vault audit log and write entries to a new file"
    )
    parser.add_argument("src", help="Source audit log file (.private_log or .gz)")
    parser.add_argument("dst", help="Destination file to write entries to")
    args = parser.parse_args()

    reader = VaultLogReader(args.src)
    with VaultLogWriter(args.dst, mode="w") as writer:
        for entry in reader:
            writer.write(entry)

    print(f"Wrote entries from {args.src} to {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
