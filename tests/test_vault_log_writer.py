import gzip
import io
import json

from vault_audit_lib import VaultLogWriter


def test_write_plain_file(tmp_path):
    file_path = tmp_path / "audit.log"
    with VaultLogWriter(str(file_path)) as writer:
        writer.write({"request": {"id": "1"}, "msg": "one"})
        writer.write("plain line")

    text = file_path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    assert json.loads(lines[0])["msg"] == "one"
    assert lines[1] == "plain line"


def test_write_gz_file(tmp_path):
    file_path = tmp_path / "audit.log.gz"
    with VaultLogWriter(str(file_path)) as writer:
        writer.write({"request": {"id": "2"}, "ok": True})

    with gzip.open(file_path, "rt", encoding="utf-8") as file_handle:
        lines = [line for line in file_handle.read().splitlines() if line.strip()]

    assert json.loads(lines[0])["request"]["id"] == "2"


def test_write_file_like():
    sio = io.StringIO()
    writer = VaultLogWriter(sio)
    writer.write({"request": {"id": "3"}, "a": 1})
    writer.write("raw")
    writer.flush()

    value = sio.getvalue()
    lines = [line for line in value.splitlines() if line.strip()]
    assert json.loads(lines[0])["a"] == 1
    assert lines[1] == "raw"
