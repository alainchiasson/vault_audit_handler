from vault_audit_lib import VaultLogReader

for entry in VaultLogReader(".private_log/vault_audit_sample.json"):
    # entry is a dict if the line was JSON, otherwise a str
    print(entry)
