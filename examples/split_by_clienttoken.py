#!/usr/bin/env python3
"""Split transactions into files per `auth.client_token`.

This example reads a Vault audit log (or .private_log) and writes one
output file per distinct `auth.client_token` encountered. Output files
are placed in an output directory and named using a sanitized version
of the client token.
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


def _extract_client_token_from_entry(entry) -> str | None:
    """Return `auth.client_token` if present (top-level `auth` field only).

    The client token must come from the top-level `auth` field per requirement.
    """
    if not isinstance(entry, dict):
        return None
    auth = entry.get("auth")
    if isinstance(auth, dict):
        ct = auth.get("client_token")
        if isinstance(ct, str):
            return ct
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Split transactions per client token")
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
            # try to find a client token in any entry of the transaction
            client_token = None
            for e in entries:
                ct = _extract_client_token_from_entry(e)
                if ct:
                    client_token = ct
                    break

            if not client_token:
                # write transactions without auth.client_token to a dedicated error file
                if error_writer is None:
                    fname = "error_no_token.json"
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

            if client_token not in writers:
                fname = _sanitized_filename(client_token) + ".jsonl"
                out_path = os.path.join(args.out_dir, fname)
                # choose file mode: if overwriting requested, use 'w', else append
                mode = args.mode
                if mode == "a" and os.path.exists(out_path):
                    use_mode = "a"
                else:
                    use_mode = mode
                writers[client_token] = VaultTransactionWriter(out_path, mode=use_mode)

            writer = writers[client_token]
            writer.write_transaction(request_id, entries)
            counts[client_token] += 1

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
    for token, c in counts.items():
        if token == error_key:
            print(f"- no-token: {c} transactions (written to error_no_token.json)")
        else:
            print(f"- {token}: {c} transactions")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
