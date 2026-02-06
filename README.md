# vault_audit_log_manipulate

Utilities to read, filter, split, and write Vault audit logs and transactions.

## Overview

This repository provides small Python utilities and a library (`src/vault_audit_lib`) for parsing and manipulating HashiCorp Vault audit log files and transaction data. The `examples/` directory contains quick scripts demonstrating common tasks.

## Requirements

- Python 3.8+ (recommended)
- See `requirements.txt` for runtime dependencies and `requirements-dev.txt` for development/test dependencies.

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

## Usage

- Library: Import the package from `src/vault_audit_lib` in your code.
- Examples: Run one of the example scripts in the `examples/` directory. For example:

```bash
python examples/read_vault_log.py path/to/audit.log
python examples/split_by_clienttoken.py path/to/audit.log
```

## Tests

Run tests with `pytest`:

```bash
pytest -q
```

## Contributing

Contributions and issues are welcome. Please follow the existing code style and include tests for new functionality.

## License

By default the repository does not include a license file. Add a `LICENSE` if you plan to open-source the project.
