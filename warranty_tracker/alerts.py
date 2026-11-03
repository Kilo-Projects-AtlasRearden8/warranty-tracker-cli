"""Expiry alert logic for warranty items."""

from datetime import date
from typing import List, Tuple

from .models import WarrantyItem


def expired_items(items: List[WarrantyItem], today: date = None) -> List[WarrantyItem]:
    today = today or date.today()
    return [item for item in items if item.is_expired(today)]


def expiring_soon_items(items: List[WarrantyItem], within_days: int = 30, today: date = None) -> List[WarrantyItem]:
    today = today or date.today()
    return [item for item in items if item.is_expiring_soon(within_days, today)]


def alert_items(items: List[WarrantyItem], within_days: int = 30, today: date = None) -> Tuple[List[WarrantyItem], List[WarrantyItem]]:
    """Return (expired, expiring_soon) lists for the given items."""
    return expired_items(items, today), expiring_soon_items(items, within_days, today)
