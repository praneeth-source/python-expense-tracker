"""
test_expense_tracker.py
-----------------------
Unit tests for expense_tracker.py using Python's built-in unittest framework.
Tests all Phase 2 functionality:
1. Adding daily expenses with amount, category, description, date.
2. Supported categories (Food, Transport, Education, Shopping, Entertainment, Healthcare, Other).
3. Viewing all recorded expenses.
4. Calculating total expenses.
5. Filtering expenses by category.
6. Validation rules (amounts, dates, categories, descriptions).
"""

from datetime import date
import unittest

import expense_tracker


class TestExpenseTrackerPhase2(unittest.TestCase):
    """Test suite for Phase 2 expense tracker functionality."""

    def setUp(self):
        """Reset the expense tracker module state before each test."""
        expense_tracker.clear_expenses()

    def tearDown(self):
        """Clean up state after each test."""
        expense_tracker.clear_expenses()

    # --- Category Tests ---

    def test_supported_categories_list(self):
        """Ensure all 7 required categories are supported."""
        expected_categories = [
            "Food",
            "Transport",
            "Education",
            "Shopping",
            "Entertainment",
            "Healthcare",
            "Other"
        ]
        actual_categories = expense_tracker.get_categories()
        self.assertEqual(actual_categories, expected_categories)

    def test_validate_category_case_insensitivity(self):
        """Ensure category validation is case-insensitive and returns canonical format."""
        self.assertEqual(expense_tracker.validate_category("food"), "Food")
        self.assertEqual(expense_tracker.validate_category("TRANSPORT"), "Transport")
        self.assertEqual(expense_tracker.validate_category("  education  "), "Education")
        self.assertEqual(expense_tracker.validate_category("Healthcare"), "Healthcare")

    def test_validate_category_invalid(self):
        """Ensure invalid or empty categories raise ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.validate_category("Investments")

        with self.assertRaises(ValueError):
            expense_tracker.validate_category("")

        with self.assertRaises(ValueError):
            expense_tracker.validate_category("   ")

    # --- Amount Validation Tests ---

    def test_validate_amount_valid_values(self):
        """Ensure positive ints, floats, and numeric strings are validated and rounded."""
        self.assertEqual(expense_tracker.validate_amount(25), 25.0)
        self.assertEqual(expense_tracker.validate_amount(19.99), 19.99)
        self.assertEqual(expense_tracker.validate_amount("42.50"), 42.50)
        self.assertEqual(expense_tracker.validate_amount(10.556), 10.56)

    def test_validate_amount_invalid_values(self):
        """Ensure zero, negative, boolean, and non-numeric amounts raise ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.validate_amount(0)

        with self.assertRaises(ValueError):
            expense_tracker.validate_amount(-15.0)

        with self.assertRaises(ValueError):
            expense_tracker.validate_amount("not_a_number")

        with self.assertRaises(ValueError):
            expense_tracker.validate_amount(True)

    # --- Description Validation Tests ---

    def test_validate_description_valid(self):
        """Ensure non-empty descriptions are stripped and accepted."""
        self.assertEqual(expense_tracker.validate_description("Grocery shopping"), "Grocery shopping")
        self.assertEqual(expense_tracker.validate_description("  Bus fare  "), "Bus fare")

    def test_validate_description_invalid(self):
        """Ensure empty or whitespace-only descriptions raise ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.validate_description("")

        with self.assertRaises(ValueError):
            expense_tracker.validate_description("   ")

    # --- Date Validation Tests ---

    def test_validate_date_valid(self):
        """Ensure valid YYYY-MM-DD dates are accepted."""
        self.assertEqual(expense_tracker.validate_date("2026-11-18"), "2026-11-18")
        self.assertEqual(expense_tracker.validate_date("2024-02-29"), "2024-02-29")  # Leap year

    def test_validate_date_invalid(self):
        """Ensure invalid formats or nonexistent dates raise ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.validate_date("18-11-2026")  # Wrong format

        with self.assertRaises(ValueError):
            expense_tracker.validate_date("2026/11/18")  # Wrong separator

        with self.assertRaises(ValueError):
            expense_tracker.validate_date("2026-02-30")  # Nonexistent day

        with self.assertRaises(ValueError):
            expense_tracker.validate_date("not-a-date")

        with self.assertRaises(ValueError):
            expense_tracker.validate_date("")

    # --- Adding Expense Tests ---

    def test_add_expense_with_explicit_date(self):
        """Ensure adding an expense with an explicit date stores all fields correctly."""
        expense = expense_tracker.add_expense(
            amount="25.50",
            category="Food",
            description="Lunch with colleagues",
            date_str="2026-11-18"
        )

        self.assertEqual(expense["amount"], 25.50)
        self.assertEqual(expense["category"], "Food")
        self.assertEqual(expense["description"], "Lunch with colleagues")
        self.assertEqual(expense["date"], "2026-11-18")

        all_expenses = expense_tracker.get_all_expenses()
        self.assertEqual(len(all_expenses), 1)
        self.assertEqual(all_expenses[0], expense)

    def test_add_expense_with_default_date(self):
        """Ensure omitting date defaults to today's date in YYYY-MM-DD format."""
        today_iso = date.today().strftime("%Y-%m-%d")
        expense = expense_tracker.add_expense(
            amount=15.0,
            category="Transport",
            description="Subway ticket"
        )
        self.assertEqual(expense["date"], today_iso)

    def test_add_expense_using_custom_list(self):
        """Ensure functions accept a custom list without mutating module list."""
        custom_list = []
        expense = expense_tracker.add_expense(
            amount=50.0,
            category="Shopping",
            description="Books",
            date_str="2026-11-18",
            expenses_list=custom_list
        )
        self.assertEqual(len(custom_list), 1)
        self.assertEqual(len(expense_tracker.get_all_expenses()), 0)

    # --- Viewing and Calculating Total Tests ---

    def test_get_all_expenses_returns_copy(self):
        """Ensure get_all_expenses returns a new list to prevent external mutation."""
        expense_tracker.add_expense(10, "Food", "Snack", "2026-11-18")
        retrieved = expense_tracker.get_all_expenses()
        retrieved.clear()
        self.assertEqual(len(expense_tracker.get_all_expenses()), 1)

    def test_calculate_total_expenses_empty(self):
        """Ensure total is 0.0 when no expenses are recorded."""
        self.assertEqual(expense_tracker.calculate_total_expenses(), 0.0)

    def test_calculate_total_expenses_multiple(self):
        """Ensure total is calculated and rounded accurately across multiple expenses."""
        expense_tracker.add_expense(12.50, "Food", "Breakfast", "2026-11-18")
        expense_tracker.add_expense(30.25, "Transport", "Train ticket", "2026-11-18")
        expense_tracker.add_expense(50.00, "Education", "Online Course", "2026-11-18")

        total = expense_tracker.calculate_total_expenses()
        self.assertEqual(total, 92.75)

    # --- Filtering Tests ---

    def test_filter_expenses_by_category(self):
        """Ensure expenses are correctly filtered by category (case-insensitive)."""
        expense_tracker.add_expense(15.00, "Food", "Lunch", "2026-11-18")
        expense_tracker.add_expense(45.00, "Food", "Dinner", "2026-11-18")
        expense_tracker.add_expense(20.00, "Transport", "Taxi", "2026-11-18")
        expense_tracker.add_expense(80.00, "Healthcare", "Medicine", "2026-11-18")

        food_expenses = expense_tracker.filter_expenses_by_category("food")
        self.assertEqual(len(food_expenses), 2)
        self.assertTrue(all(item["category"] == "Food" for item in food_expenses))

        transport_expenses = expense_tracker.filter_expenses_by_category("Transport")
        self.assertEqual(len(transport_expenses), 1)
        self.assertEqual(transport_expenses[0]["description"], "Taxi")

        entertainment = expense_tracker.filter_expenses_by_category("Entertainment")
        self.assertEqual(len(entertainment), 0)

    # --- Phase 4: Search and Date Range Tests ---

    def test_validate_date_range_valid(self):
        """Ensure valid date ranges pass validation."""
        start, end = expense_tracker.validate_date_range("2026-11-01", "2026-11-30")
        self.assertEqual(start, "2026-11-01")
        self.assertEqual(end, "2026-11-30")

        # Same start and end date is valid
        start_same, end_same = expense_tracker.validate_date_range("2026-11-18", "2026-11-18")
        self.assertEqual(start_same, end_same)

    def test_validate_date_range_inverted_raises_error(self):
        """Ensure inverted date ranges (start > end) raise ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.validate_date_range("2026-11-30", "2026-11-01")

    def test_search_expenses_by_description(self):
        """Ensure substring description search works case-insensitively."""
        expense_tracker.add_expense(25.00, "Food", "Italian dinner with team", "2026-11-18")
        expense_tracker.add_expense(12.00, "Transport", "Bus commute to work", "2026-11-18")
        expense_tracker.add_expense(15.00, "Food", "Quick lunch sandwich", "2026-11-19")

        # Case-insensitive substring searches
        results = expense_tracker.search_expenses_by_description("DINNER")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["description"], "Italian dinner with team")

        results_commute = expense_tracker.search_expenses_by_description("work")
        self.assertEqual(len(results_commute), 1)
        self.assertEqual(results_commute[0]["category"], "Transport")

        # No match
        self.assertEqual(len(expense_tracker.search_expenses_by_description("hotel")), 0)

    def test_search_expenses_by_description_empty_keyword(self):
        """Ensure searching with empty keyword raises ValueError."""
        with self.assertRaises(ValueError):
            expense_tracker.search_expenses_by_description("")

        with self.assertRaises(ValueError):
            expense_tracker.search_expenses_by_description("   ")

    def test_filter_expenses_by_date(self):
        """Ensure filtering by specific date returns only matching date records."""
        expense_tracker.add_expense(10.00, "Food", "Snack", "2026-11-17")
        expense_tracker.add_expense(20.00, "Food", "Lunch", "2026-11-18")
        expense_tracker.add_expense(30.00, "Transport", "Taxi", "2026-11-18")
        expense_tracker.add_expense(40.00, "Shopping", "Clothes", "2026-11-19")

        results = expense_tracker.filter_expenses_by_date("2026-11-18")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(item["date"] == "2026-11-18" for item in results))

        no_results = expense_tracker.filter_expenses_by_date("2026-11-20")
        self.assertEqual(len(no_results), 0)

    def test_filter_expenses_by_date_range(self):
        """Ensure filtering by date range correctly includes boundary dates and intermediate dates."""
        expense_tracker.add_expense(10.00, "Food", "Early snack", "2026-11-05")
        expense_tracker.add_expense(20.00, "Food", "Lunch", "2026-11-10")
        expense_tracker.add_expense(30.00, "Transport", "Train", "2026-11-15")
        expense_tracker.add_expense(40.00, "Shopping", "Shoes", "2026-11-20")
        expense_tracker.add_expense(50.00, "Other", "Gift", "2026-11-25")

        # Range from 2026-11-10 to 2026-11-20 inclusive
        range_results = expense_tracker.filter_expenses_by_date_range("2026-11-10", "2026-11-20")
        self.assertEqual(len(range_results), 3)
        self.assertEqual(range_results[0]["date"], "2026-11-10")
        self.assertEqual(range_results[1]["date"], "2026-11-15")
        self.assertEqual(range_results[2]["date"], "2026-11-20")

    def test_display_total_spending_for_filtered_results(self):
        """Ensure total spending calculation is accurate for filtered results."""
        expense_tracker.add_expense(15.50, "Food", "Breakfast", "2026-11-18")
        expense_tracker.add_expense(34.50, "Food", "Dinner", "2026-11-18")
        expense_tracker.add_expense(50.00, "Transport", "Fuel", "2026-11-18")

        food_items = expense_tracker.filter_expenses_by_category("Food")
        filtered_total = expense_tracker.calculate_total_expenses(food_items)
        self.assertEqual(filtered_total, 50.00)

    # --- Phase 5: Financial Summary & Analytics Tests ---

    def test_calculate_monthly_summary_empty(self):
        """Ensure monthly summary returns empty dict for empty dataset."""
        self.assertEqual(expense_tracker.calculate_monthly_summary(), {})

    def test_calculate_monthly_summary_multiple_months(self):
        """Ensure expenses are grouped and totaled correctly across multiple months."""
        expense_tracker.add_expense(100.00, "Shopping", "Clothes", "2026-09-15")
        expense_tracker.add_expense(50.00, "Food", "Groceries", "2026-10-02")
        expense_tracker.add_expense(75.50, "Transport", "Train", "2026-10-20")
        expense_tracker.add_expense(200.00, "Education", "Tuition", "2026-11-05")

        summary = expense_tracker.calculate_monthly_summary()
        expected = {
            "2026-09": 100.00,
            "2026-10": 125.50,
            "2026-11": 200.00
        }
        self.assertEqual(summary, expected)

    def test_calculate_category_summary_empty(self):
        """Ensure category summary returns empty dict for empty dataset."""
        self.assertEqual(expense_tracker.calculate_category_summary(), {})

    def test_calculate_category_summary_totals(self):
        """Ensure category totals accurately sum expenses per category."""
        expense_tracker.add_expense(20.00, "Food", "Lunch", "2026-11-18")
        expense_tracker.add_expense(30.00, "Food", "Dinner", "2026-11-18")
        expense_tracker.add_expense(45.00, "Transport", "Cab", "2026-11-18")

        summary = expense_tracker.calculate_category_summary()
        self.assertEqual(summary["Food"], 50.00)
        self.assertEqual(summary["Transport"], 45.00)

    def test_get_highest_spending_category_empty(self):
        """Ensure highest spending category on empty dataset returns (None, 0.0)."""
        cat, amt = expense_tracker.get_highest_spending_category()
        self.assertIsNone(cat)
        self.assertEqual(amt, 0.0)

    def test_get_highest_spending_category(self):
        """Ensure highest spending category is correctly identified."""
        expense_tracker.add_expense(15.00, "Food", "Snack", "2026-11-18")
        expense_tracker.add_expense(120.00, "Education", "Books", "2026-11-18")
        expense_tracker.add_expense(50.00, "Food", "Dinner", "2026-11-18")

        cat, amt = expense_tracker.get_highest_spending_category()
        self.assertEqual(cat, "Education")
        self.assertEqual(amt, 120.00)

    def test_calculate_daily_summary_empty(self):
        """Ensure daily summary on date with no expenses returns (0.0, 0, [])."""
        total, count, matching = expense_tracker.calculate_daily_summary("2026-11-18")
        self.assertEqual(total, 0.0)
        self.assertEqual(count, 0)
        self.assertEqual(matching, [])

    def test_calculate_daily_summary_populated(self):
        """Ensure daily summary accurately totals spending and counts for a specific date."""
        expense_tracker.add_expense(15.00, "Food", "Lunch", "2026-11-18")
        expense_tracker.add_expense(25.00, "Transport", "Taxi", "2026-11-18")
        expense_tracker.add_expense(50.00, "Shopping", "Shirt", "2026-11-19")

        total, count, matching = expense_tracker.calculate_daily_summary("2026-11-18")
        self.assertEqual(total, 40.00)
        self.assertEqual(count, 2)
        self.assertEqual(len(matching), 2)

    def test_get_highest_expense_empty(self):
        """Ensure highest expense returns None when dataset is empty."""
        self.assertIsNone(expense_tracker.get_highest_expense())

    def test_get_highest_expense_populated(self):
        """Ensure highest individual expense transaction is correctly identified."""
        expense_tracker.add_expense(10.00, "Food", "Snack", "2026-11-18")
        expense_tracker.add_expense(150.00, "Shopping", "Watch", "2026-11-18")
        expense_tracker.add_expense(45.00, "Transport", "Train", "2026-11-18")

        highest = expense_tracker.get_highest_expense()
        self.assertIsNotNone(highest)
        self.assertEqual(highest["amount"], 150.00)
        self.assertEqual(highest["description"], "Watch")

    def test_calculate_average_expense_empty(self):
        """Ensure average expense returns 0.0 when dataset is empty."""
        self.assertEqual(expense_tracker.calculate_average_expense(), 0.0)

    def test_calculate_average_expense_populated(self):
        """Ensure average expense per transaction is calculated accurately."""
        expense_tracker.add_expense(10.00, "Food", "A", "2026-11-18")
        expense_tracker.add_expense(20.00, "Transport", "B", "2026-11-18")
        expense_tracker.add_expense(30.00, "Shopping", "C", "2026-11-18")

        avg = expense_tracker.calculate_average_expense()
        self.assertEqual(avg, 20.00)

    def test_get_financial_overview_empty(self):
        """Ensure overview returns zeroed values and None for empty dataset."""
        overview = expense_tracker.get_financial_overview()
        self.assertEqual(overview["total_expenses"], 0.0)
        self.assertEqual(overview["transaction_count"], 0)
        self.assertEqual(overview["average_expense"], 0.0)
        self.assertIsNone(overview["highest_expense"])

    def test_get_financial_overview_populated(self):
        """Ensure complete financial overview contains all metrics."""
        expense_tracker.add_expense(25.00, "Food", "Lunch", "2026-11-18")
        expense_tracker.add_expense(75.00, "Education", "Course", "2026-11-18")

        overview = expense_tracker.get_financial_overview()
        self.assertEqual(overview["total_expenses"], 100.00)
        self.assertEqual(overview["transaction_count"], 2)
        self.assertEqual(overview["average_expense"], 50.00)
        self.assertEqual(overview["highest_expense"]["amount"], 75.00)

    # --- Helper & Formatting Tests ---

    def test_format_expense(self):
        """Ensure format_expense creates readable string containing all details."""
        exp = {
            "date": "2026-11-18",
            "category": "Entertainment",
            "amount": 14.50,
            "description": "Cinema ticket"
        }
        formatted = expense_tracker.format_expense(exp)
        self.assertIn("2026-11-18", formatted)
        self.assertIn("Entertainment", formatted)
        self.assertIn("$   14.50", formatted)
        self.assertIn("Cinema ticket", formatted)


if __name__ == "__main__":
    unittest.main()
