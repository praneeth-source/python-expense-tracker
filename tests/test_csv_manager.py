"""
test_csv_manager.py
-------------------
Unit tests for csv_manager.py using Python's built-in unittest framework.
Covers all Phase 3 requirements:
- CSV file creation.
- Writing single and multiple expenses.
- Reading saved expenses.
- Calculating total expenses directly from CSV.
- Category-based filtering from CSV.
- Empty CSV file handling.
- Missing file handling (graceful degradation without crashes).
- Preventing duplicate headers on append.
- Application restart persistence simulation.
- Compatibility with expense_tracker.py.
"""

import csv
import os
import tempfile
import unittest

import csv_manager
import expense_tracker


class TestCSVManagerPhase3(unittest.TestCase):
    """Test suite for Phase 3 CSV persistence and management."""

    def setUp(self):
        """Set up an isolated temporary directory for test CSV operations."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_csv = os.path.join(self.temp_dir.name, "test_expenses.csv")
        self.missing_csv = os.path.join(self.temp_dir.name, "non_existent.csv")

    def tearDown(self):
        """Clean up temporary directory and files."""
        self.temp_dir.cleanup()

    # --- 1. CSV Creation & Header Tests ---

    def test_get_headers(self):
        """Verify standard CSV headers match specification."""
        expected = ["Date", "Category", "Amount", "Description"]
        self.assertEqual(csv_manager.get_headers(), expected)

    def test_csv_file_creation(self):
        """Verify initialize_csv creates file with proper headers if missing."""
        self.assertFalse(os.path.exists(self.temp_csv))
        created = csv_manager.initialize_csv(self.temp_csv)

        self.assertTrue(created)
        self.assertTrue(os.path.exists(self.temp_csv))

        with open(self.temp_csv, mode="r", newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 1)
            self.assertEqual(reader[0], ["Date", "Category", "Amount", "Description"])

    def test_prevent_duplicate_headers_on_append(self):
        """Ensure appending new records never duplicates the header row."""
        csv_manager.initialize_csv(self.temp_csv)

        # Append two records
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 12.50, "description": "Lunch"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 5.00, "description": "Bus"},
            filepath=self.temp_csv
        )

        with open(self.temp_csv, mode="r", newline="", encoding="utf-8") as f:
            lines = list(csv.reader(f))
            # Line 1: Header, Line 2: Expense 1, Line 3: Expense 2
            self.assertEqual(len(lines), 3)
            self.assertEqual(lines[0], ["Date", "Category", "Amount", "Description"])
            self.assertEqual(lines[1], ["2026-11-18", "Food", "12.50", "Lunch"])
            self.assertEqual(lines[2], ["2026-11-18", "Transport", "5.00", "Bus"])

    # --- 2. Writing Multiple Expenses ---

    def test_write_multiple_expenses(self):
        """Verify saving a list of multiple expenses works correctly."""
        expenses = [
            {"date": "2026-11-18", "category": "Food", "amount": 25.00, "description": "Groceries"},
            {"date": "2026-11-18", "category": "Education", "amount": 120.00, "description": "Textbook"},
            {"date": "2026-11-19", "category": "Entertainment", "amount": 15.75, "description": "Movie"},
        ]
        saved_count = csv_manager.save_multiple_expenses(expenses, filepath=self.temp_csv)
        self.assertEqual(saved_count, 3)

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["category"], "Food")
        self.assertEqual(records[1]["amount"], 120.00)
        self.assertEqual(records[2]["description"], "Movie")

    # --- 3. Reading Saved Expenses ---

    def test_read_saved_expenses(self):
        """Verify reading records returns properly typed dictionaries."""
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Healthcare", "amount": 45.20, "description": "Medicine"},
            filepath=self.temp_csv
        )

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(records), 1)

        record = records[0]
        self.assertIsInstance(record["amount"], float)
        self.assertEqual(record["amount"], 45.20)
        self.assertEqual(record["date"], "2026-11-18")
        self.assertEqual(record["category"], "Healthcare")
        self.assertEqual(record["description"], "Medicine")

    # --- 4. Total Calculation Directly from CSV ---

    def test_calculate_total_from_csv(self):
        """Verify total expenses are correctly calculated directly from CSV file."""
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 10.25, "description": "Coffee"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Shopping", "amount": 39.75, "description": "Shoes"},
            filepath=self.temp_csv
        )

        total = csv_manager.calculate_total_from_csv(filepath=self.temp_csv)
        self.assertEqual(total, 50.00)

    # --- 5. Category Filtering Directly from CSV ---

    def test_filter_expenses_by_category_from_csv(self):
        """Verify category filtering works case-insensitively from CSV records."""
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 15.00, "description": "Breakfast"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 22.00, "description": "Train"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 25.00, "description": "Dinner"},
            filepath=self.temp_csv
        )

        # Case-insensitive check
        food_records = csv_manager.filter_expenses_by_category_from_csv("food", filepath=self.temp_csv)
        self.assertEqual(len(food_records), 2)
        self.assertTrue(all(r["category"] == "Food" for r in food_records))

        # Check non-existent category in file
        edu_records = csv_manager.filter_expenses_by_category_from_csv("Education", filepath=self.temp_csv)
        self.assertEqual(len(edu_records), 0)

    # --- 6. Empty File Handling ---

    def test_empty_csv_file_handling(self):
        """Ensure reading, calculating total, and filtering on empty file return empty/zero without errors."""
        # Create an empty 0-byte file
        with open(self.temp_csv, mode="w", encoding="utf-8") as f:
            pass
        self.assertEqual(os.path.getsize(self.temp_csv), 0)

        records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(records, [])

        total = csv_manager.calculate_total_from_csv(filepath=self.temp_csv)
        self.assertEqual(total, 0.0)

        filtered = csv_manager.filter_expenses_by_category_from_csv("Food", filepath=self.temp_csv)
        self.assertEqual(filtered, [])

    # --- 7. Missing File Handling (Graceful Degradation) ---

    def test_missing_csv_file_handling(self):
        """Ensure non-existent files do not crash the application."""
        self.assertFalse(os.path.exists(self.missing_csv))

        # read_expenses should return empty list
        records = csv_manager.read_expenses(filepath=self.missing_csv)
        self.assertEqual(records, [])

        # calculate_total_from_csv should return 0.0
        total = csv_manager.calculate_total_from_csv(filepath=self.missing_csv)
        self.assertEqual(total, 0.0)

        # filter should return empty list
        filtered = csv_manager.filter_expenses_by_category_from_csv("Food", filepath=self.missing_csv)
        self.assertEqual(filtered, [])

    def test_append_to_missing_file_creates_and_saves(self):
        """Ensure appending to a missing file path creates it with headers automatically."""
        self.assertFalse(os.path.exists(self.missing_csv))
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 14.00, "description": "Metro"},
            filepath=self.missing_csv
        )

        self.assertTrue(os.path.exists(self.missing_csv))
        records = csv_manager.read_expenses(filepath=self.missing_csv)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["description"], "Metro")

    # --- 8. Persistence After Restarting the Application ---

    def test_persistence_after_application_restart(self):
        """
        Simulate an application lifecycle:
        1. Application session 1 adds records to CSV and terminates.
        2. Application session 2 starts with a fresh environment and reads the CSV.
        3. All records, amounts, and filters match persistent storage.
        """
        # Session 1: Write records
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Education", "amount": 85.00, "description": "Workshop"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 18.50, "description": "Lunch"},
            filepath=self.temp_csv
        )

        # Session 2: Fresh read (simulating restart)
        fresh_records = csv_manager.read_expenses(filepath=self.temp_csv)
        fresh_total = csv_manager.calculate_total_from_csv(filepath=self.temp_csv)
        fresh_edu = csv_manager.filter_expenses_by_category_from_csv("Education", filepath=self.temp_csv)

        self.assertEqual(len(fresh_records), 2)
        self.assertEqual(fresh_total, 103.50)
        self.assertEqual(len(fresh_edu), 1)
        self.assertEqual(fresh_edu[0]["amount"], 85.00)

    # --- 9. Compatibility with expense_tracker.py ---

    def test_expense_tracker_csv_integration(self):
        """Verify expense_tracker.py can record directly to CSV and load from CSV."""
        expense_tracker.clear_expenses()

        # Add expense via expense_tracker with save_to_csv=True
        exp = expense_tracker.add_expense(
            amount=32.00,
            category="Shopping",
            description="Jeans",
            date_str="2026-11-18",
            save_to_csv=True,
            csv_filepath=self.temp_csv
        )

        # Verify persisted in CSV
        csv_records = csv_manager.read_expenses(filepath=self.temp_csv)
        self.assertEqual(len(csv_records), 1)
        self.assertEqual(csv_records[0]["amount"], 32.00)
        self.assertEqual(csv_records[0]["description"], "Jeans")

        # Clear memory and reload from CSV
        expense_tracker.clear_expenses()
        self.assertEqual(len(expense_tracker.get_all_expenses()), 0)

        loaded = expense_tracker.load_from_csv(filepath=self.temp_csv)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["amount"], 32.00)

    # --- 10. Phase 4: CSV Search, Date Filtering, and Filtered Total ---

    def test_search_expenses_by_description_from_csv(self):
        """Verify keyword search in description directly from CSV."""
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Food", "amount": 18.00, "description": "Team lunch pizza"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 25.00, "description": "Airport taxi"},
            filepath=self.temp_csv
        )

        matches = csv_manager.search_expenses_by_description_from_csv("PIZZA", filepath=self.temp_csv)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["description"], "Team lunch pizza")

        no_matches = csv_manager.search_expenses_by_description_from_csv("train", filepath=self.temp_csv)
        self.assertEqual(len(no_matches), 0)

    def test_filter_expenses_by_date_from_csv(self):
        """Verify filtering by specific date directly from CSV."""
        csv_manager.append_expense(
            {"date": "2026-11-17", "category": "Food", "amount": 10.00, "description": "Snack"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-18", "category": "Transport", "amount": 20.00, "description": "Gas"},
            filepath=self.temp_csv
        )

        matches = csv_manager.filter_expenses_by_date_from_csv("2026-11-18", filepath=self.temp_csv)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["amount"], 20.00)

    def test_filter_expenses_by_date_range_from_csv(self):
        """Verify filtering by date range directly from CSV."""
        csv_manager.append_expense(
            {"date": "2026-11-01", "category": "Utilities", "amount": 100.00, "description": "Electricity"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-15", "category": "Food", "amount": 40.00, "description": "Groceries"},
            filepath=self.temp_csv
        )
        csv_manager.append_expense(
            {"date": "2026-11-30", "category": "Entertainment", "amount": 25.00, "description": "Concert"},
            filepath=self.temp_csv
        )

        # Range 2026-11-10 to 2026-11-20
        matches = csv_manager.filter_expenses_by_date_range_from_csv("2026-11-10", "2026-11-20", filepath=self.temp_csv)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["description"], "Groceries")

    def test_calculate_filtered_total(self):
        """Verify calculate_filtered_total correctly sums any list of records."""
        records = [
            {"amount": 15.25},
            {"amount": 34.75},
            {"amount": 10.00}
        ]
        self.assertEqual(csv_manager.calculate_filtered_total(records), 60.00)
        self.assertEqual(csv_manager.calculate_filtered_total([]), 0.0)

    def test_search_and_filter_missing_file_graceful(self):
        """Ensure search and date filters handle missing CSV file without errors."""
        self.assertEqual(csv_manager.search_expenses_by_description_from_csv("test", filepath=self.missing_csv), [])
        self.assertEqual(csv_manager.filter_expenses_by_date_from_csv("2026-11-18", filepath=self.missing_csv), [])
        self.assertEqual(csv_manager.filter_expenses_by_date_range_from_csv("2026-11-01", "2026-11-30", filepath=self.missing_csv), [])

    # --- 11. Phase 5: CSV Financial Summary & Analytics Tests ---

    def test_get_monthly_summary_from_csv(self):
        """Verify monthly expense totals calculated directly from CSV file."""
        csv_manager.append_expense({"date": "2026-08-10", "category": "Food", "amount": 20.00, "description": "Lunch"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-08-25", "category": "Transport", "amount": 30.00, "description": "Bus"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-09-05", "category": "Shopping", "amount": 100.00, "description": "Clothes"}, filepath=self.temp_csv)

        summary = csv_manager.get_monthly_summary_from_csv(filepath=self.temp_csv)
        self.assertEqual(summary, {"2026-08": 50.00, "2026-09": 100.00})

    def test_get_category_summary_from_csv(self):
        """Verify category spending totals calculated directly from CSV file."""
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 15.00, "description": "Lunch"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 35.00, "description": "Dinner"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Healthcare", "amount": 80.00, "description": "Dentist"}, filepath=self.temp_csv)

        cat_summary = csv_manager.get_category_summary_from_csv(filepath=self.temp_csv)
        self.assertEqual(cat_summary["Food"], 50.00)
        self.assertEqual(cat_summary["Healthcare"], 80.00)

    def test_get_highest_spending_category_from_csv(self):
        """Verify top spending category identified directly from CSV file."""
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 20.00, "description": "A"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Education", "amount": 150.00, "description": "B"}, filepath=self.temp_csv)

        top_cat, top_amt = csv_manager.get_highest_spending_category_from_csv(filepath=self.temp_csv)
        self.assertEqual(top_cat, "Education")
        self.assertEqual(top_amt, 150.00)

    def test_get_daily_summary_from_csv(self):
        """Verify daily spending total and count calculated directly from CSV file."""
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 10.00, "description": "A"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Transport", "amount": 15.00, "description": "B"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-19", "category": "Food", "amount": 50.00, "description": "C"}, filepath=self.temp_csv)

        total, count, records = csv_manager.get_daily_summary_from_csv("2026-11-18", filepath=self.temp_csv)
        self.assertEqual(total, 25.00)
        self.assertEqual(count, 2)
        self.assertEqual(len(records), 2)

    def test_get_highest_and_average_expense_from_csv(self):
        """Verify highest expense and average calculation from CSV records."""
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 20.00, "description": "Snack"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Shopping", "amount": 80.00, "description": "Jacket"}, filepath=self.temp_csv)

        highest = csv_manager.get_highest_expense_from_csv(filepath=self.temp_csv)
        self.assertEqual(highest["amount"], 80.00)
        self.assertEqual(highest["description"], "Jacket")

        avg = csv_manager.get_average_expense_from_csv(filepath=self.temp_csv)
        self.assertEqual(avg, 50.00)

    def test_get_financial_overview_from_csv(self):
        """Verify complete financial overview metrics from CSV file."""
        csv_manager.append_expense({"date": "2026-11-18", "category": "Food", "amount": 30.00, "description": "A"}, filepath=self.temp_csv)
        csv_manager.append_expense({"date": "2026-11-18", "category": "Transport", "amount": 70.00, "description": "B"}, filepath=self.temp_csv)

        overview = csv_manager.get_financial_overview_from_csv(filepath=self.temp_csv)
        self.assertEqual(overview["total_expenses"], 100.00)
        self.assertEqual(overview["transaction_count"], 2)
        self.assertEqual(overview["average_expense"], 50.00)
        self.assertEqual(overview["highest_expense"]["amount"], 70.00)

    def test_analytics_empty_and_missing_csv_file(self):
        """Ensure all analytics functions handle empty and non-existent files gracefully without errors."""
        # Test on missing file
        self.assertEqual(csv_manager.get_monthly_summary_from_csv(filepath=self.missing_csv), {})
        self.assertEqual(csv_manager.get_category_summary_from_csv(filepath=self.missing_csv), {})
        self.assertEqual(csv_manager.get_highest_spending_category_from_csv(filepath=self.missing_csv), (None, 0.0))
        self.assertEqual(csv_manager.get_daily_summary_from_csv("2026-11-18", filepath=self.missing_csv), (0.0, 0, []))
        self.assertIsNone(csv_manager.get_highest_expense_from_csv(filepath=self.missing_csv))
        self.assertEqual(csv_manager.get_average_expense_from_csv(filepath=self.missing_csv), 0.0)

        overview_missing = csv_manager.get_financial_overview_from_csv(filepath=self.missing_csv)
        self.assertEqual(overview_missing["total_expenses"], 0.0)
        self.assertEqual(overview_missing["transaction_count"], 0)
        self.assertEqual(overview_missing["average_expense"], 0.0)
        self.assertIsNone(overview_missing["highest_expense"])

        # Test on 0-byte empty file
        with open(self.temp_csv, mode="w", encoding="utf-8") as f:
            pass
        self.assertEqual(csv_manager.get_monthly_summary_from_csv(filepath=self.temp_csv), {})
        self.assertEqual(csv_manager.get_highest_spending_category_from_csv(filepath=self.temp_csv), (None, 0.0))
        self.assertEqual(csv_manager.get_average_expense_from_csv(filepath=self.temp_csv), 0.0)


if __name__ == "__main__":
    unittest.main()
