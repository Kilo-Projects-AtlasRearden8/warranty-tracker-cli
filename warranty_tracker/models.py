"""Data models and date logic for warranty items."""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from typing import Optional


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day


def add_months(d: date, months: int) -> date:
    """Add whole months to a date, clamping the day to month length."""
    total_months = d.year * 12 + (d.month - 1) + months
    year, month = divmod(total_months, 12)
    month += 1
    day = min(d.day, _days_in_month(year, month))
    return date(year, month, day)


@dataclass
class WarrantyItem:
    id: str
    name: str
    category: str
    purchased: str  # ISO date string (YYYY-MM-DD)
    warranty_years: int = 1
    warranty_months: int = 0
    warranty_days: int = 0
    serial: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def expiry_date(self) -> date:
        """Return the warranty expiration date."""
        purchased = date.fromisoformat(self.purchased)
        d = purchased
        if self.warranty_years:
            d = date(d.year + self.warranty_years, d.month, min(d.day, _days_in_month(d.year + self.warranty_years, d.month)))
        if self.warranty_months:
            d = add_months(d, self.warranty_months)
        if self.warranty_days:
            d = d + timedelta(days=self.warranty_days)
        return d

    def days_until_expiry(self, today: Optional[date] = None) -> int:
        today = today or date.today()
        return (self.expiry_date() - today).days

    def is_expired(self, today: Optional[date] = None) -> bool:
        return self.days_until_expiry(today) < 0

    def is_expiring_soon(self, within_days: int = 30, today: Optional[date] = None) -> bool:
        days = self.days_until_expiry(today)
        return 0 <= days <= within_days

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WarrantyItem":
        return cls(**data)
