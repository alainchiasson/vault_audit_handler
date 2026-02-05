#!/usr/bin/env python3
"""Split transactions into files per `auth.entity_id`.

This example reads a Vault audit log (or .private_log) and writes one
output file per distinct `auth.entity_id` encountered. Output files
are placed in an output directory and named using a sanitized version
of the entity ID.
"""
from __future__ import annotations

import argparse
import os
import re
from collections import defaultdict
from typing import Dict

from vault_audit_lib import VaultTransactionReader, VaultTransactionWriter


def _sanitized_filename(token: str) -> str:
    # replace any character not allowed in simple filenames with '_'
    s = re.sub(r"[^A-Za-z0-9._-]", "_", token)
    # keep it reasonably short
    return s[:200]


def _extract_entity_id_from_entry(entry) -> str | None:
    """Return `auth.entity_id` if present (top-level `auth` field only).

    The entity ID must come from the top-level `auth` field per requirement.
    """
    if not isinstance(entry, dict):
        return None
    auth = entry.get("auth")
    if isinstance(auth, dict):
        eid = auth.get("entity_id")
        if isinstance(eid, str):
            return eid
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Split transactions per entity ID")
    parser.add_argument("path", help="Path to the audit log file (.private_log or .gz)")
    parser.add_argument("out_dir", help="Directory to place per-token output files")
    parser.add_argument(
        "--mode",
        choices=("a", "w"),
        default="a",
        help="Open mode for per-token files: 'w' to overwrite, 'a' to append (default: a)",
    )
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    reader = VaultTransactionReader(args.path)

    writers: Dict[str, VaultTransactionWriter] = {}
    counts = defaultdict(int)
    error_writer: VaultTransactionWriter | None = None
    error_key = "error_no_token"

    try:
        for request_id, entries in reader:
            # try to find an entity ID in any entry of the transaction
            entity_id = None
            for e in entries:
                eid = _extract_entity_id_from_entry(e)
                if eid:
                    entity_id = eid
                    break

            if not entity_id:
                # write transactions without auth.entity_id to a dedicated error file
                if error_writer is None:
                    fname = "error_no_entity_id.json"
                    out_path = os.path.join(args.out_dir, fname)
                    mode = args.mode
                    if mode == "a" and os.path.exists(out_path):
                        use_mode = "a"
                    else:
                        use_mode = mode
                    error_writer = VaultTransactionWriter(out_path, mode=use_mode)
                error_writer.write_transaction(request_id, entries)
                counts[error_key] += 1
                continue

            if entity_id not in writers:
                fname = _sanitized_filename(entity_id) + ".jsonl"
                out_path = os.path.join(args.out_dir, fname)
                # choose file mode: if overwriting requested, use 'w', else append
                mode = args.mode
                if mode == "a" and os.path.exists(out_path):
                    use_mode = "a"
                else:
                    use_mode = mode
                writers[entity_id] = VaultTransactionWriter(out_path, mode=use_mode)
            writer = writers[entity_id]
            writer.write_transaction(request_id, entries)
            counts[entity_id] += 1

    finally:
        # close all writers
        for w in writers.values():
            try:
                w.close()
            except Exception:
                pass
            if error_writer is not None:
                try:
                    error_writer.close()
                except Exception:
                    pass

    total_writers = len(writers)
    total_tx = sum(counts.values())
    print(
        f"Wrote {total_tx} transactions into {total_writers} files under {args.out_dir}"
    )
    for entity_id, c in counts.items():
        if entity_id == error_key:
            print(
                f"- no-entity_id: {c} transactions (written to error_no_entity_id.json)"
            )
        else:
            print(f"- {entity_id}: {c} transactions")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
