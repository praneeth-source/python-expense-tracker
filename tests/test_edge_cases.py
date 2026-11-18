"""
test_edge_cases.py
------------------
Specialized edge-case and robustness tests for Personal Expense Tracker.
Covers:
1. Corrupted CSV rows (malformed columns, non-numeric values, negative values, empty cells).
2. Binary / encoding anomalies in CSV storage.
3. Missing newlines before appending.
4. Input validation boundaries (high-precision amounts, whitespace padding, leap years).
5. Analytics edge cases (single-item datasets, tied maximums, uniform categories).
"""

import csv
import os
import tempfile
import unittest

import csv_manager
import expense_tracker


class TestEdgeCasesAndHardening(unittest.TestCase):
    """Test suite for edge cases, corrupted files, and data hardening."""

    def setUp(self):
        """Set up an isolated temporary directory for test CSV operations."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_csv = os.path.join(self.temp_dir.name, "edge_case_expenses.csv")

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    # --- 1. Corrupted CSV Handling Tests ---

    def test_corrupted_csv_skips_bad_rows(self):
        """
        Verify read_expenses safely skips corrupted or malformed rows:
        - Line 2: Missing columns
        - Line 3: Non-numeric amount
        - Line 4: Valid row
        - Line 5: Negative amount
        - Line 6: Blank line
        - Line 7: Valid row
        """
        corrupted_content = (
            "Date,Category,Amount,Description\n"
            "2026-11-18,Food\n"                                # Too few columns
            "2026-11-18,Food,NOT_A_NUMBER,Invalid\n"           # Non-numeric amount
            "2026-11-18,Food,25.00,Good Lunch\n"               # Valid
            "2026-11-18,Transport,-10.00,Negative\n"           # Negative amount
            "\n"                                               # Blank line
            "   ,   ,   ,   \n"                                # Whitespace only
            "2026-11-19,Shopping,50.00,Good Jacket\n"          # Valid
        )
        with open(self.temp_csv, mode="w", encoding="utf-8") as f:
            f.write(corrupted_content)

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["description"], "Good Lunch")
        self.assertEqual(records[0]["amount"], 25.00)
        self.assertEqual(records[1]["description"], "Good Jacket")
        self.assertEqual(records[1]["amount"], 50.00)

    def test_corrupted_csv_without_headers(self):
        """Verify an uninitialized or broken header row does not crash the reader."""
        with open(self.temp_csv, mode="w", encoding="utf-8") as f:
            f.write("")

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(records, [])

    # --- 2. Data Safety: Non-destructive Appending & Trailing Newlines ---

    def test_append_to_file_without_trailing_newline(self):
        """
        Ensure appending to a CSV file missing a trailing newline does not
        merge the last row with the new row.
        """
        # Write header and 1 row without trailing newline
        with open(self.temp_csv, mode="w", encoding="utf-8") as f:
            f.write("Date,Category,Amount,Description\n2026-11-18,Food,10.00,Coffee")

        # Append new expense
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 5.00, "description": "Bus"},
            filepath=self.temp_csv
        )

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["description"], "Coffee")
        self.assertEqual(records[1]["description"], "Bus")

    def test_data_safety_never_overwrites_existing_records(self):
        """Ensure repeated appends preserve all previous entries exactly."""
        for i in range(1, 6):
            csv_manager.append_expense(
                {"date": f"2026-11-0{i}", "category": "Food", "amount": float(i * 10), "description": f"Expense {i}"},
                filepath=self.temp_csv
            )

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(records), 5)
        for i in range(1, 6):
            self.assertEqual(records[i - 1]["description"], f"Expense {i}")
            self.assertEqual(records[i - 1]["amount"], float(i * 10))

    # --- 3. Input Validation Boundaries ---

    def test_amount_validation_whitespace_and_high_precision(self):
        """Ensure amounts with surrounding whitespace or extra decimal places round accurately."""
        self.assertEqual(expense_tracker.validate_amount("  34.567  "), 34.57)
        self.assertEqual(expense_tracker.validate_amount("  0.01  "), 0.01)

    def test_leap_year_date_validation(self):
        """Ensure leap days are accepted in leap years and rejected in non-leap years."""
        self.assertEqual(expense_tracker.validate_date("2024-02-29"), "2024-02-29")
        with self.assertRaises(ValueError):
            expense_tracker.validate_date("2023-02-29")

    def test_category_validation_mixed_casing_and_spaces(self):
        """Ensure category validation handles mixed case and whitespace correctly."""
        self.assertEqual(expense_tracker.validate_category("   eNtErTaInMeNt   "), "Entertainment")
        self.assertEqual(expense_tracker.validate_category("hEaLtHcArE"), "Healthcare")

    def test_date_range_same_day(self):
        """Ensure a date range where start equals end matches only that single day."""
        test_expenses = [
            {"date": "2026-11-17", "category": "Food", "amount": 10.00, "description": "Day before"},
            {"date": "2026-11-18", "category": "Food", "amount": 20.00, "description": "Target day"},
            {"date": "2026-11-19", "category": "Food", "amount": 30.00, "description": "Day after"}
        ]
        matched = expense_tracker.filter_expenses_by_date_range(
            "2026-11-18", "2026-11-18", expenses_list=test_expenses
        )
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["description"], "Target day")

    # --- 4. Analytics Edge Cases ---

    def test_analytics_single_transaction_dataset(self):
        """Verify analytics metrics on a dataset with exactly 1 transaction."""
        single_list = [
            {"date": "2026-11-18", "category": "Education", "amount": 99.99, "description": "Book"}
        ]
        overview = expense_tracker.get_financial_overview(expenses_list=single_list)
        self.assertEqual(overview["total_expenses"], 99.99)
        self.assertEqual(overview["transaction_count"], 1)
        self.assertEqual(overview["average_expense"], 99.99)
        self.assertEqual(overview["highest_expense"]["amount"], 99.99)

        cat, amt = expense_tracker.get_highest_spending_category(expenses_list=single_list)
        self.assertEqual(cat, "Education")
        self.assertEqual(amt, 99.99)

    def test_analytics_tied_highest_expenses(self):
        """Ensure get_highest_expense returns a valid record when multiple expenses tie for highest."""
        tied_list = [
            {"date": "2026-11-18", "category": "Food", "amount": 50.00, "description": "Lunch A"},
            {"date": "2026-11-19", "category": "Transport", "amount": 50.00, "description": "Ticket B"},
            {"date": "2026-11-20", "category": "Shopping", "amount": 20.00, "description": "Snack C"}
        ]
        highest = expense_tracker.get_highest_expense(expenses_list=tied_list)
        self.assertEqual(highest["amount"], 50.00)


if __name__ == "__main__":
    unittest.main()
