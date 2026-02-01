from vault_audit_lib import VaultTransactionReader


def test_group_by_request_id():
    entries = [
        {"request": {"id": "a"}, "type": "request"},
        {"request": {"id": "a"}, "message": "step1"},
        {"request": {"id": "a"}, "response": {"status": 200}},
        {"request": {"id": "b"}, "type": "request"},
        {"request": {"id": "b"}, "response": {"status": 204}},
    ]

    reader = VaultTransactionReader(entries)
    transactions = list(reader)

    assert len(transactions) == 2

    rid0, entries0 = transactions[0]
    rid1, entries1 = transactions[1]

    assert rid0 == "a"
    assert len(entries0) == 3

    assert rid1 == "b"
    assert len(entries1) == 2
