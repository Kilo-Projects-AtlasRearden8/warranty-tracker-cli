# Warranty Tracker CLI

Keep track of warranties and expiration dates for your appliances,
electronics, and gear — all on your own computer, with no accounts, no
API keys, and nothing sent to the cloud.

This is a small, practical tool from **Asdale Dynamics, LLC**, built to be
beginner friendly, clearly tested, and local first. If you can open a
terminal, you can use it.

## What it does

- **Add** a warranty item: name, category, purchase date, and how long the
  warranty lasts (years, months, or days)
- **See** when each item expires and how many days are left
- **Know** at a glance what's expired and what's expiring soon
- **Export** your list to CSV or JSON so you can open it in a spreadsheet
  or back it up
- **Store** everything in one local JSON file on your machine — nothing
  leaves your computer

## Who this is for

This tool is for anyone who owns things with warranties and would like a
simple place to keep track of them. It's part of the small-business and
life-admin work we do at Asdale Dynamics, LLC (Indiana, formed October
2026), alongside beginner-friendly AI guides and practical tools you can
actually use. Learn more about the LLC at dylanasdale.github.io and in
_The Massive AI Manual_.

## Install

```bash
pip install .
```

That's it. It installs a `warranty-tracker` command you can run from
anywhere. No sign-up, no credit card, no API key.

If you'd rather not install, you can run it straight from this folder:

```bash
python -m warranty_tracker add --name "Refrigerator" --purchased 2025-01-15 --warranty-years 2
```

## Add your first item

```bash
warranty-tracker add \
  --name "Refrigerator" \
  --category appliance \
  --purchased 2025-01-15 \
  --warranty-years 2 \
  --serial SN12345 \
  --notes "Kitchen fridge"
```

You'll get back an ID for the item. Keep that ID handy — you'll use it to
edit or remove the item later.

`--warranty-years`, `--warranty-months`, and `--warranty-days` can be
combined. So a 1-year-and-3-month warranty looks like:

```bash
warranty-tracker add --name "Laptop" --warranty-years 1 --warranty-months 3
```

## See your items

```bash
warranty-tracker list
```

You'll see the ID, name, category, purchase date, expiration date, days
left, and status (ok / expiring soon / expired) for every item.

Only want one category?

```bash
warranty-tracker list --category electronics
```

Only expired?

```bash
warranty-tracker list --expired
```

Only expiring within the next 30 days?

```bash
warranty-tracker list --expiring
```

## Get expiry alerts

```bash
warranty-tracker alerts
```

This shows anything that's already expired, plus anything expiring within
the next 30 days. Change the window with `--within`:

```bash
warranty-tracker alerts --within 60
```

If everything's current, it'll tell you so.

## Edit or remove an item

```bash
warranty-tracker edit --id <id> --name "Freezer" --warranty-years 3
warranty-tracker remove --id <id>
```

## Export your list

To a CSV (opens in Excel, Google Sheets, Numbers, etc.):

```bash
warranty-tracker export --format csv --out my-warranties.csv
```

To JSON:

```bash
warranty-tracker export --format json --out my-warranties.json
```

## Where your data lives

By default, your warranties are stored in
`~/.warranty-tracker/warranties.json` on your computer. That's it — one
file, yours, local.

You can put it somewhere else with `--store`:

```bash
warranty-tracker --store ./warranties.json add --name "Microwave"
```

Or set the `WARRANTY_TRACKER_FILE` environment variable:

```bash
export WARRANTY_TRACKER_FILE=./warranties.json
warranty-tracker add --name "Microwave"
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```

There are 25 tests covering the date math (leap years, month rollover,
expiration boundaries), local storage, and the commands.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC makes practical, beginner-friendly tools and guides
— from AI education to small-business helpers like this one. Founded by
Dylan Asdale, a registered nurse turned AI author. Learn more at
dylanasdale.github.io and in _The Massive AI Manual_.

This tool is practical software. It is not medical advice.
