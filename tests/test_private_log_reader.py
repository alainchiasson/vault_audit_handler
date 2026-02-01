import json

from vault_audit_lib import VaultLogReader


def test_read_json_and_plain_lines(tmp_path):
    p = tmp_path / "sample.private_log"
    lines = [
        json.dumps({"type": "login", "user": "alice"}),
        "this is not json",
        json.dumps({"type": "logout", "user": "alice"}),
    ]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    reader = VaultLogReader(str(p))
    entries = list(reader)

    assert isinstance(entries[0], dict)
    assert entries[0]["type"] == "login"

    assert isinstance(entries[1], str)
    assert entries[1] == "this is not json"

    assert isinstance(entries[2], dict)
    assert entries[2]["type"] == "logout"
