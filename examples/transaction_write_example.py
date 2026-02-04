#!/usr/bin/env python3
"""Example: read transactions and write them as ordered log entries.

Reads transactions via `VaultTransactionReader` and writes their
entries merged by `time` using `VaultTransactionWriter`.

Usage:
  python examples/transaction_write_example.py input.private_log out.private_log
"""
from __future__ import annotations

import argparse

from vault_audit_lib import VaultTransactionReader, VaultTransactionWriter


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge transactions into time-ordered log file"
    )
    parser.add_argument("src", help="Source audit log file (path or .gz)")
    parser.add_argument("dst", help="Destination file to write merged entries")
    parser.add_argument(
        "--time-key",
        default="time",
        help="Key name for entry timestamp (default: time)",
    )
    args = parser.parse_args()

    reader = VaultTransactionReader(args.src)

    with VaultTransactionWriter(args.dst, mode="w") as writer:
        writer.write_transactions(reader, time_key=args.time_key)

    print(f"Wrote merged transactions from {args.src} -> {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
