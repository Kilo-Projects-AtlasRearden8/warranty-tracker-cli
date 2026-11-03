"""Command-line interface for the warranty tracker."""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

from .models import WarrantyItem
from .storage import WarrantyStore, default_storage_path
from .alerts import expired_items, expiring_soon_items, alert_items


def _parse_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date '{value}': expected YYYY-MM-DD") from exc
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="warranty-tracker",
        description="Track warranties and expiration dates for appliances, electronics, and gear. Local JSON storage, no keys required.",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help=f"Path to the JSON storage file (default: {default_storage_path()}, or WARRANTY_TRACKER_FILE)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a warranty item")
    add_p.add_argument("--name", required=True, help="Item name (e.g. Refrigerator)")
    add_p.add_argument("--category", default="general", help="Category (default: general)")
    add_p.add_argument("--purchased", type=_parse_date, default=date.today().isoformat(), help="Purchase date YYYY-MM-DD (default: today)")
    add_p.add_argument("--warranty-years", type=int, default=1, help="Warranty length in years (default: 1)")
    add_p.add_argument("--warranty-months", type=int, default=0, help="Additional warranty months (default: 0)")
    add_p.add_argument("--warranty-days", type=int, default=0, help="Additional warranty days (default: 0)")
    add_p.add_argument("--serial", default=None, help="Serial number")
    add_p.add_argument("--notes", default=None, help="Notes")

    list_p = sub.add_parser("list", help="List warranty items")
    list_p.add_argument("--category", default=None, help="Filter by category")
    list_p.add_argument("--expired", action="store_true", help="Show only expired items")
    list_p.add_argument("--expiring", action="store_true", help="Show only items expiring within 30 days")

    remove_p = sub.add_parser("remove", help="Remove a warranty item by id")
    remove_p.add_argument("--id", required=True, help="Item id")

    edit_p = sub.add_parser("edit", help="Edit an existing warranty item by id")
    edit_p.add_argument("--id", required=True, help="Item id")
    edit_p.add_argument("--name", default=None, help="Item name")
    edit_p.add_argument("--category", default=None, help="Category")
    edit_p.add_argument("--purchased", type=_parse_date, default=None, help="Purchase date YYYY-MM-DD")
    edit_p.add_argument("--warranty-years", type=int, default=None, help="Warranty length in years")
    edit_p.add_argument("--warranty-months", type=int, default=None, help="Additional warranty months")
    edit_p.add_argument("--warranty-days", type=int, default=None, help="Additional warranty days")
    edit_p.add_argument("--serial", default=None, help="Serial number")
    edit_p.add_argument("--notes", default=None, help="Notes")

    export_p = sub.add_parser("export", help="Export items to CSV or JSON")
    export_p.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format (default: csv)")
    export_p.add_argument("--out", type=Path, default=Path("warranty_export.csv"), help="Output file (default: warranty_export.csv)")

    alerts_p = sub.add_parser("alerts", help="Show expired and soon-expiring items")
    alerts_p.add_argument("--within", type=int, default=30, help="Days ahead to treat as expiring soon (default: 30)")

    return parser


def _print_table(items: List[WarrantyItem]) -> None:
    if not items:
        print("No warranty items found.")
        return
    header = f"{'ID':<8} {'NAME':<24} {'CATEGORY':<14} {'PURCHASED':<12} {'EXPIRES':<12} {'DAYS LEFT':<10} {'STATUS'}"
    print(header)
    print("-" * len(header))
    today = date.today()
    for item in items:
        expires = item.expiry_date().isoformat()
        days = item.days_until_expiry(today)
        if item.is_expired(today):
            status = "EXPIRED"
        elif item.is_expiring_soon(30, today):
            status = "EXPIRING SOON"
        else:
            status = "ok"
        print(f"{item.id[:8]:<8} {item.name:<24} {item.category:<14} {item.purchased:<12} {expires:<12} {days:<10} {status}")


def cmd_add(args: argparse.Namespace, store: WarrantyStore) -> int:
    item = WarrantyItem(
        id="",
        name=args.name,
        category=args.category,
        purchased=args.purchased,
        warranty_years=args.warranty_years,
        warranty_months=args.warranty_months,
        warranty_days=args.warranty_days,
        serial=args.serial,
        notes=args.notes,
    )
    store.add(item)
    print(f"Added warranty item {item.id} for '{item.name}' (expires {item.expiry_date().isoformat()}).")
    return 0


def cmd_list(args: argparse.Namespace, store: WarrantyStore) -> int:
    items = store.load()
    if args.category:
        items = [item for item in items if item.category == args.category]
    today = date.today()
    if args.expired:
        items = [item for item in items if item.is_expired(today)]
    if args.expiring:
        items = [item for item in items if item.is_expiring_soon(30, today) and not item.is_expired(today)]
    items.sort(key=lambda item: (item.purchased, item.name))
    _print_table(items)
    return 0


def cmd_remove(args: argparse.Namespace, store: WarrantyStore) -> int:
    if store.remove(args.id):
        print(f"Removed warranty item {args.id}.")
        return 0
    print(f"No warranty item found with id {args.id}.", file=sys.stderr)
    return 1


def cmd_edit(args: argparse.Namespace, store: WarrantyStore) -> int:
    fields = {}
    if args.name is not None:
        fields["name"] = args.name
    if args.category is not None:
        fields["category"] = args.category
    if args.purchased is not None:
        fields["purchased"] = args.purchased
    if args.warranty_years is not None:
        fields["warranty_years"] = args.warranty_years
    if args.warranty_months is not None:
        fields["warranty_months"] = args.warranty_months
    if args.warranty_days is not None:
        fields["warranty_days"] = args.warranty_days
    if args.serial is not None:
        fields["serial"] = args.serial
    if args.notes is not None:
        fields["notes"] = args.notes

    if not fields:
        print("No fields to update.", file=sys.stderr)
        return 1

    updated = store.update(args.id, **fields)
    if updated is None:
        print(f"No warranty item found with id {args.id}.", file=sys.stderr)
        return 1
    print(f"Updated warranty item {updated.id} for '{updated.name}' (expires {updated.expiry_date().isoformat()}).")
    return 0


def cmd_export(args: argparse.Namespace, store: WarrantyStore) -> int:
    items = store.load()
    items.sort(key=lambda item: (item.purchased, item.name))
    today = date.today()
    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        import json
        with out_path.open("w", encoding="utf-8") as handle:
            json.dump([item.to_dict() for item in items], handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        fields = [
            "id", "name", "category", "purchased", "warranty_years",
            "warranty_months", "warranty_days", "serial", "notes",
            "expires", "days_until_expiry", "status", "created_at",
        ]
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            for item in items:
                days = item.days_until_expiry(today)
                if item.is_expired(today):
                    status = "EXPIRED"
                elif item.is_expiring_soon(30, today):
                    status = "EXPIRING SOON"
                else:
                    status = "ok"
                writer.writerow([
                    item.id, item.name, item.category, item.purchased,
                    item.warranty_years, item.warranty_months, item.warranty_days,
                    item.serial or "", item.notes or "", item.expiry_date().isoformat(),
                    days, status, item.created_at,
                ])
    print(f"Exported {len(items)} item(s) to {out_path} ({args.format}).")
    return 0


def cmd_alerts(args: argparse.Namespace, store: WarrantyStore) -> int:
    items = store.load()
    today = date.today()
    expired, soon = alert_items(items, args.within, today)
    if not expired and not soon:
        print("No alerts. All warranties are current.")
        return 0
    if expired:
        print("=== EXPIRED WARRANTIES ===")
        _print_table(expired)
        print()
    if soon:
        print(f"=== EXPIRING WITHIN {args.within} DAYS ===")
        _print_table(soon)
    return 0


_COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "remove": cmd_remove,
    "edit": cmd_edit,
    "export": cmd_export,
    "alerts": cmd_alerts,
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    store = WarrantyStore(args.store)
    handler = _COMMANDS[args.command]
    try:
        return handler(args, store)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
