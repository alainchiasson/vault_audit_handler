#!/usr/bin/env python3
"""Read a Vault audit log and write entries to a new file.

Usage:
  python examples/read_and_write_vault_log.py input.private_log output.private_log
"""
from __future__ import annotations

import argparse

from vault_audit_lib import VaultEventFilter, VaultLogReader, VaultLogWriter


# Map function to extract relevant fields
def map(ev):
    nev = {
        "time": ev.get("time"),
        "type": ev.get("type"),
        "request_id": ev.get("request", {}).get("id"),
        "auth_entity_id": ev.get("auth", {}).get("entity_id"),
        "auth_client_token": ev.get("auth", {}).get("client_token"),
        "namespace": ev.get("request", {}).get("namespace", {}).get("path"),
        "mount_type": ev.get("request", {}).get("mount_type"),
        "request_path": ev.get("request", {}).get("path"),
    }
    return nev


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a Vault audit log and write entries to a new file"
    )
    parser.add_argument("src", help="Source audit log file (.private_log or .gz)")
    parser.add_argument("dst", help="Destination file to write entries to")
    args = parser.parse_args()

    reader = VaultLogReader(args.src)
    nerr = VaultEventFilter("error", lambda v: v is None)
    filt = VaultEventFilter("type", "response")

    with VaultLogWriter(args.dst, mode="w") as writer:
        for entry in reader:
            # only write entries that are of type "response" and have no error
            if filt.match(entry) and nerr.match(entry):
                writer.write(map(entry))

    print(f"Wrote entries from {args.src} to {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
