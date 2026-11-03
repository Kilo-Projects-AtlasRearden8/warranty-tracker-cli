"""Tests for warranty date logic."""

import unittest
from datetime import date

from warranty_tracker.models import WarrantyItem, add_months


class ExpiryDateTests(unittest.TestCase):
    def test_basic_years(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2025-01-15", warranty_years=2)
        self.assertEqual(item.expiry_date(), date(2027, 1, 15))

    def test_years_leap_day(self):
        item = WarrantyItem(id="1", name="Gear", category="gear", purchased="2024-02-29", warranty_years=1)
        self.assertEqual(item.expiry_date(), date(2025, 2, 28))

    def test_months_rollover(self):
        item = WarrantyItem(id="1", name="TV", category="electronics", purchased="2025-01-31", warranty_years=0, warranty_months=1)
        self.assertEqual(item.expiry_date(), date(2025, 2, 28))

    def test_months_year_rollover(self):
        item = WarrantyItem(id="1", name="TV", category="electronics", purchased="2025-11-05", warranty_years=0, warranty_months=14)
        self.assertEqual(item.expiry_date(), date(2027, 1, 5))

    def test_combined_years_months_days(self):
        item = WarrantyItem(id="1", name="Laptop", category="electronics", purchased="2025-03-10", warranty_years=1, warranty_months=2, warranty_days=5)
        self.assertEqual(item.expiry_date(), date(2026, 5, 15))

    def test_days_only(self):
        item = WarrantyItem(id="1", name="Tool", category="gear", purchased="2025-06-01", warranty_years=0, warranty_days=90)
        self.assertEqual(item.expiry_date(), date(2025, 8, 30))


class DaysUntilExpiryTests(unittest.TestCase):
    def test_future_item_positive_days(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2025-01-01", warranty_years=1)
        self.assertGreater(item.days_until_expiry(date(2025, 6, 1)), 0)

    def test_expired_item_negative_days(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2023-01-01", warranty_years=1)
        self.assertLess(item.days_until_expiry(date(2025, 1, 1)), 0)

    def test_expiry_day_zero_days(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2024-01-01", warranty_years=1)
        self.assertEqual(item.days_until_expiry(date(2025, 1, 1)), 0)


class StatusTests(unittest.TestCase):
    def test_is_expired(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2023-01-01", warranty_years=1)
        self.assertTrue(item.is_expired(date(2025, 2, 1)))
        self.assertFalse(item.is_expired(date(2023, 12, 31)))

    def test_is_expiring_soon_boundary(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2025-01-01", warranty_years=1)
        # expires 2026-01-01; within 30 days of 2025-12-02 -> True, of 2025-12-01 -> False
        self.assertTrue(item.is_expiring_soon(30, date(2025, 12, 2)))
        self.assertFalse(item.is_expiring_soon(30, date(2025, 12, 1)))

    def test_expired_item_not_expiring_soon(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2023-01-01", warranty_years=1)
        self.assertFalse(item.is_expiring_soon(30, date(2025, 2, 1)))


class SerializationTests(unittest.TestCase):
    def test_to_from_dict_roundtrip(self):
        original = WarrantyItem(id="abc", name="Microwave", category="appliance", purchased="2025-05-05", warranty_years=1, serial="SN123", notes="kitchen")
        restored = WarrantyItem.from_dict(original.to_dict())
        self.assertEqual(restored, original)
        self.assertEqual(restored.expiry_date(), date(2026, 5, 5))


if __name__ == "__main__":
    unittest.main()
