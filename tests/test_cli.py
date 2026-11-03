"""Tests for the CLI entry point."""

import unittest
from unittest.mock import patch

from warranty_tracker.cli import main


class CLITests(unittest.TestCase):
    def test_add_prints_confirmation(self):
        with patch("warranty_tracker.cli.WarrantyStore") as mock_store:
            instance = mock_store.return_value
            with patch("builtins.print") as mock_print:
                code = main(["add", "--name", "Fridge", "--category", "appliance", "--purchased", "2025-01-15", "--warranty-years", "2"])
                self.assertEqual(code, 0)
                instance.add.assert_called_once()
                added = instance.add.call_args[0][0]
                self.assertEqual(added.name, "Fridge")
                self.assertEqual(added.expiry_date().isoformat(), "2027-01-15")
                self.assertTrue(any("Added" in str(call) for call in mock_print.call_args_list))

    def test_alerts_no_alerts(self):
        with patch("warranty_tracker.cli.WarrantyStore") as mock_store:
            instance = mock_store.return_value
            instance.load.return_value = []
            with patch("builtins.print") as mock_print:
                code = main(["alerts"])
                self.assertEqual(code, 0)
                self.assertTrue(any("No alerts" in str(call) for call in mock_print.call_args_list))

    def test_remove_missing_returns_error(self):
        with patch("warranty_tracker.cli.WarrantyStore") as mock_store:
            instance = mock_store.return_value
            instance.remove.return_value = False
            code = main(["remove", "--id", "nope"])
            self.assertEqual(code, 1)

    def test_export_csv_writes_file(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "out.csv"
            with patch("warranty_tracker.cli.WarrantyStore") as mock_store:
                instance = mock_store.return_value
                instance.load.return_value = []
                code = main(["export", "--format", "csv", "--out", str(out)])
                self.assertEqual(code, 0)
                self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
