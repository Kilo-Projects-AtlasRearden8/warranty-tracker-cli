# STATUS

## What was built

`warranty-tracker` — a local-first Python CLI for tracking warranties and
expiration dates for appliances, electronics, and gear. No accounts, no API
keys, no cloud, no personal data leaves the machine. Zero dependencies
(Python standard library only).

Package layout:

- `warranty_tracker/models.py` — `WarrantyItem` dataclass and date logic:
  expiration date (purchased + years/months/days, with month rollover and
  day clamping), days until expiry, expired/expiring-soon checks
- `warranty_tracker/storage.py` — `WarrantyStore`: atomic JSON read/write,
  add, remove, find; storage path via `--store` or `WARRANTY_TRACKER_FILE`,
  default `~/.warranty-tracker/warranties.json`
- `warranty_tracker/alerts.py` — expired and expiring-soon item selection
- `warranty_tracker/cli.py` — argparse CLI: `add`, `list`, `remove`,
  `export` (CSV/JSON), `alerts`
- `tests/` — 25 unittest tests covering date logic (leap years, month
  rollover, expiry boundaries), storage round-trip/corruption/remove, and CLI
  behavior
- `LICENSE` — MIT, copyright `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — install, usage, credits Asdale Dynamics, LLC
- `pyproject.toml` — installs the `warranty-tracker` console script

Built and committed by Dylan Asdale / Asdale Dynamics, LLC. Credited in the
README and LICENSE as Asdale Dynamics, LLC.

## How to run

```bash
pip install .                                   # installs warranty-tracker
# or, without installing:
# python -m warranty_tracker <command>

warranty-tracker add --name "Refrigerator" --category appliance \
  --purchased 2025-01-15 --warranty-years 2 --serial SN12345
warranty-tracker list
warranty-tracker list --expired
warranty-tracker alerts --within 60
warranty-tracker remove --id <id>
warranty-tracker export --format csv --out warranties.csv

WARRANTY_TRACKER_FILE=./warranties.json warranty-tracker add --name "Microwave"
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Verification results

- `pip install .` — successful (wheel built and installed)
- `python -m unittest discover -s tests` — **25 tests OK** (date logic,
  storage, CLI)
- CLI smoke test — `add`, `list` (with category/expired filters), `alerts`,
  `export --format csv` all run correctly; computed dates verified by hand
  (e.g. 2025-01-15 + 2 years = 2027-01-15)
- `warranty-tracker --help` — runs cleanly
- LICENSE copyright line verified exactly:
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- Git initialized and committed as `cf5a443` (master, root commit), plain
  commit message, no Co-authored-by trailer, no push, no remote
- No `.github/workflows` files; no secrets, API keys, or personal data in any
  file

## Known gaps

- No edit command for existing items (remove and re-add instead)
- Categories are free-text strings (no predefined list)
- Single JSON file storage; no file locking (single-user, local-first by
  design)
- Alerts print to stdout only; no email/desktop notification backend
- Tests use stdlib `unittest` only; no pytest/tox configuration
- Packaging tested with `pip install .` on CPython 3.13; requires Python >= 3.8
