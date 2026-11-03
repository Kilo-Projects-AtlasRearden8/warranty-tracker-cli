"""Tests for local JSON storage."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from warranty_tracker.models import WarrantyItem
from warranty_tracker.storage import WarrantyStore


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "warranties.json"
        self.store = WarrantyStore(self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_empty_store_returns_empty_list(self):
        self.assertEqual(self.store.load(), [])

    def test_add_and_load_roundtrip(self):
        item = WarrantyItem(id="1", name="Fridge", category="appliance", purchased="2025-01-15", warranty_years=2)
        self.store.add(item)
        loaded = self.store.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "Fridge")
        self.assertEqual(loaded[0].expiry_date().isoformat(), "2027-01-15")

    def test_persistence_across_stores(self):
        item = WarrantyItem(id="2", name="Laptop", category="electronics", purchased="2025-03-01", warranty_years=1)
        self.store.add(item)
        second = WarrantyStore(self.path)
        self.assertEqual(len(second.load()), 1)
        self.assertEqual(second.load()[0].id, "2")

    def test_remove_existing(self):
        self.store.add(WarrantyItem(id="1", name="A", category="general", purchased="2025-01-01"))
        self.store.add(WarrantyItem(id="2", name="B", category="general", purchased="2025-01-01"))
        self.assertTrue(self.store.remove("1"))
        self.assertEqual(len(self.store.load()), 1)
        self.assertEqual(self.store.load()[0].id, "2")

    def test_remove_missing_returns_false(self):
        self.assertFalse(self.store.remove("nonexistent"))

    def test_find(self):
        item = WarrantyItem(id="3", name="Tool", category="gear", purchased="2025-06-01", warranty_days=90)
        self.store.add(item)
        found = self.store.find("3")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Tool")
        self.assertIsNone(self.store.find("missing"))

    def test_corrupt_file_returns_empty(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{not valid json", encoding="utf-8")
        self.assertEqual(self.store.load(), [])


class DefaultPathTests(unittest.TestCase):
    def test_env_override(self):
        os.environ["WARRANTY_TRACKER_FILE"] = "/tmp/warranty-tracker-test-env.json"
        try:
            store = WarrantyStore()
            self.assertEqual(store.path, Path("/tmp/warranty-tracker-test-env.json"))
        finally:
            del os.environ["WARRANTY_TRACKER_FILE"]


if __name__ == "__main__":
    unittest.main()
