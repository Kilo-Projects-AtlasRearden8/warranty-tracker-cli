# Warranty Tracker CLI

A local-first Python command-line tool to track warranties and expiration dates
for appliances, electronics, and gear. Data lives in a local JSON file on your
machine — no accounts, no API keys, no cloud, no personal data leaves your
computer.

Built and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026),
founded by Dylan Asdale, registered nurse turned AI author. Practical, beginner
friendly, tested, local first.

## Features

- Add warranty items with name, category, purchase date, and warranty length
  (years, months, or days)
- Expiration dates computed automatically from purchase date plus warranty
  length
- List all items with days remaining and status (ok / expiring soon / expired)
- Expiry alerts: see expired items and items expiring within a chosen window
  (default 30 days)
- Export to CSV or JSON
- Local JSON storage (path configurable via `--store` or the
  `WARRANTY_TRACKER_FILE` environment variable)
- Zero dependencies — Python standard library only
- Tested date logic (leap years, month rollover, expiry boundaries)

## Install

```bash
git clone <this-repo>
cd warranty-tracker-cli
pip install .
```

This installs the `warranty-tracker` command. You can also run it without
installing:

```bash
python -m warranty_tracker add --name "Refrigerator" --category appliance --purchased 2025-01-15 --warranty-years 2
```

## Usage

Add an item:

```bash
warranty-tracker add --name "Refrigerator" --category appliance \
  --purchased 2025-01-15 --warranty-years 2 --serial SN12345 \
  --notes "Kitchen fridge"
```

List items:

```bash
warranty-tracker list
warranty-tracker list --category electronics
warranty-tracker list --expired
```

Check expiry alerts (expired + expiring within 30 days):

```bash
warranty-tracker alerts
warranty-tracker alerts --within 60
```

Remove an item:

```bash
warranty-tracker remove --id <id>
```

Export to CSV:

```bash
warranty-tracker export --format csv --out warranties.csv
```

Storage location defaults to `~/.warranty-tracker/warranties.json`. Override
with `--store` or `WARRANTY_TRACKER_FILE`:

```bash
export WARRANTY_TRACKER_FILE=./warranties.json
warranty-tracker add --name "Microwave" --warranty-years 1
```

## Run the tests

```bash
pip install .  # or run from the source tree
python -m unittest discover -s tests -v
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Asdale Dynamics, LLC makes beginner-friendly AI education, practical open-source
tools, and small-business helpers — from KDP book publishing and reselling
tooling to accessible life-admin organizers like this one. Learn more at
dylanasdale.github.io and in _The Massive AI Manual_.

This tool is educational and practical software. It is not medical advice.
