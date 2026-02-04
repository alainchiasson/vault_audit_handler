#!/usr/bin/env python3
"""Print transactions that contain any event with `error` present.

For each matching transaction the script prints the `request_id` and
each event from the transaction that contains an `error` value.
"""
from __future__ import annotations

import argparse
import json

from vault_audit_lib import (
    VaultEventFilter,
    VaultTransactionReader,
    VaultTransactionWriter,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print transactions containing error events"
    )
    parser.add_argument("path", help="Path to the audit log file (.private_log or .gz)")
    parser.add_argument(
        "--out", "-o", help="Optional destination file to write matching transactions"
    )
    args = parser.parse_args()

    reader = VaultTransactionReader(args.path)
    filt = VaultEventFilter("error", lambda v: v is not None)

    if args.out:
        written = 0
        with VaultTransactionWriter(args.out, mode="w") as writer:
            for tx in reader:
                request_id, entries = tx
                if filt.match(tx):
                    writer.write_transaction(request_id, entries)
                    written += 1
        print(f"Wrote {written} matching transactions to {args.out}")
    else:
        for tx in reader:
            # tx may be (request_id, entries)
            request_id, entries = tx
            # If any event in the transaction matches, print matching events
            if filt.match(tx):
                print(f"Transaction {request_id}:")
                for ev in entries:
                    if filt.match(ev):
                        if isinstance(ev, dict):
                            print(json.dumps(ev, ensure_ascii=False))
                        else:
                            print(ev)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
