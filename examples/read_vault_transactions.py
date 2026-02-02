#!/usr/bin/env python3
"""Simple example: group Vault log events into transactions and print them."""
from __future__ import annotations

import argparse
import json

from vault_audit_lib import VaultLogReader, VaultTransactionReader


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a Vault audit log and print transactions grouped by request.id"
    )
    parser.add_argument(
        "path", help="Path to the audit log file (.private_log or .private_log.gz)"
    )
    args = parser.parse_args()

    reader = VaultLogReader(args.path)
    txn_reader = VaultTransactionReader(reader)

    for request_id, events in txn_reader:
        print(f"Transaction {request_id}: {len(events)} events")
        for ev in events:
            print(json.dumps(ev, ensure_ascii=False))
        print("---")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
