from vault_audit_lib import VaultLogReader, VaultTransactionReader

for entry in VaultLogReader(".private_log/vault_audit_sample.json"):
    # entry is a dict if the line was JSON, otherwise a str
    print(entry)

for transaction in VaultTransactionReader(".private_log/vault_audit_sample.json"):
    request_id, entries = transaction
    print(f"Transaction {request_id} has {len(entries)} entries : {entries[0]['time']}")
