"""
main.py
-------
Main application entry point for the Personal Expense Tracker.

Provides a beginner-friendly, resilient command-line interface for:
1. Adding daily expenses with input validation and instant CSV persistence.
2. Viewing all saved expenses in a formatted tabular list.
3. Filtering expenses by category (with category total).
4. Searching expenses by description keyword (with search results total).
5. Filtering expenses by a specific date (with date total).
6. Filtering expenses by a chronological date range (with range total).
7. Comprehensive Financial Summary & Analytics dashboard (Overview, Category Analytics, Monthly Breakdown).
8. Daily Expense Summary for any selected calendar date.
9. Clean application exit.

Technical Highlights:
- Python standard library only (no external packages).
- Graceful handling of KeyboardInterrupt (Ctrl+C) and EOFError.
- While-loop input validation for reliable data entry.
- Direct persistence and resilience across application sessions.
"""

import sys
import csv_manager
import expense_tracker


def safe_input(prompt_text):
    """
    Prompt the user for input while safely handling KeyboardInterrupt and EOFError.

    Args:
        prompt_text (str): The prompt message to display.

    Returns:
        str or None: The stripped input string, or None if cancelled by the user.
    """
    try:
        return input(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n[INFO] Operation cancelled by user.")
        return None


def display_menu():
    """Print the interactive main menu options with clean visual borders."""
    print("\n" + "=" * 58)
    print("           PERSONAL EXPENSE TRACKER - MAIN MENU           ")
    print("=" * 58)
    print("  1. Add New Expense")
    print("  2. View All Saved Expenses")
    print("  3. Filter Expenses by Category")
    print("  4. Search Expenses by Description")
    print("  5. Filter Expenses by Specific Date")
    print("  6. Filter Expenses by Date Range")
    print("  7. Financial Summary & Analytics Dashboard")
    print("  8. Daily Expense Summary")
    print("  9. Exit Application")
    print("-" * 58)


def display_expenses_list(expenses, header_title):
    """
    Display a list of expenses with row numbering and total spending sum.

    Args:
        expenses (list): List of expense dictionaries.
        header_title (str): Title heading to display above the list.
    """
    print(f"\n--- {header_title} ---")
    if not expenses:
        print("  No matching expenses found.")
        return

    for idx, exp in enumerate(expenses, start=1):
        print(f"  {idx:>2}. {csv_manager.format_csv_expense(exp)}")

    total = csv_manager.calculate_filtered_total(expenses)
    print("-" * 58)
    print(f"  Total Matching Records : {len(expenses)}")
    print(f"  Total Spending Amount  : ${total:.2f}")


def handle_add_expense():
    """
    Prompt the user for expense details with while-loop validation and save to CSV.
    Safely cancels and returns to menu if user interrupts with Ctrl+C.
    """
    print("\n--- Add New Expense ---")

    # 1. Expense Amount
    while True:
        amount_input = safe_input("Enter expense amount ($): ")
        if amount_input is None:
            return
        try:
            amount = expense_tracker.validate_amount(amount_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    # 2. Category
    categories = expense_tracker.get_categories()
    print(f"Supported categories: {', '.join(categories)}")
    while True:
        category_input = safe_input("Enter category: ")
        if category_input is None:
            return
        try:
            category = expense_tracker.validate_category(category_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    # 3. Description
    while True:
        description_input = safe_input("Enter description: ")
        if description_input is None:
            return
        try:
            description = expense_tracker.validate_description(description_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    # 4. Date (optional, defaults to today)
    while True:
        date_input = safe_input("Enter date (YYYY-MM-DD) [press Enter for today]: ")
        if date_input is None:
            return
        if not date_input:
            date_val = None
            break
        try:
            date_val = expense_tracker.validate_date(date_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    # Persist validated expense
    new_expense = expense_tracker.add_expense(
        amount=amount,
        category=category,
        description=description,
        date_str=date_val,
        save_to_csv=True
    )
    print("\n[SUCCESS] Expense recorded and saved to expenses.csv:")
    print(f"  {expense_tracker.format_expense(new_expense)}")


def handle_view_all():
    """Read and display all previously saved expenses directly from CSV."""
    expenses = csv_manager.read_expenses()
    display_expenses_list(expenses, "All Saved Expenses (from expenses.csv)")


def handle_filter_by_category():
    """Prompt for category with while loop validation and display matching records with total."""
    print("\n--- Filter Expenses by Category ---")
    categories = expense_tracker.get_categories()
    print(f"Supported categories: {', '.join(categories)}")

    while True:
        category_input = safe_input("Enter category to filter: ")
        if category_input is None:
            return
        try:
            category = expense_tracker.validate_category(category_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    filtered = csv_manager.filter_expenses_by_category_from_csv(category)
    display_expenses_list(filtered, f"Expenses in Category '{category}'")


def handle_search_by_description():
    """Prompt for search keyword with while loop validation and search descriptions."""
    print("\n--- Search Expenses by Description ---")

    while True:
        keyword = safe_input("Enter search keyword: ")
        if keyword is None:
            return
        if keyword:
            break
        print("[!] Search keyword cannot be empty. Please try again.")

    results = csv_manager.search_expenses_by_description_from_csv(keyword)
    display_expenses_list(results, f"Search Results for '{keyword}'")


def handle_filter_by_date():
    """Prompt for a specific date with while loop validation and display matching expenses."""
    print("\n--- Filter Expenses by Specific Date ---")

    while True:
        date_input = safe_input("Enter date to filter (YYYY-MM-DD): ")
        if date_input is None:
            return
        try:
            target_date = expense_tracker.validate_date(date_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    filtered = csv_manager.filter_expenses_by_date_from_csv(target_date)
    display_expenses_list(filtered, f"Expenses on Date '{target_date}'")


def handle_filter_by_date_range():
    """Prompt for start and end dates with while loop validation and filter records within range."""
    print("\n--- Filter Expenses by Date Range ---")

    while True:
        while True:
            start_input = safe_input("Enter start date (YYYY-MM-DD): ")
            if start_input is None:
                return
            try:
                start_date = expense_tracker.validate_date(start_input)
                break
            except ValueError as err:
                print(f"[!] {err} Please try again.")

        while True:
            end_input = safe_input("Enter end date (YYYY-MM-DD): ")
            if end_input is None:
                return
            try:
                end_date = expense_tracker.validate_date(end_input)
                break
            except ValueError as err:
                print(f"[!] {err} Please try again.")

        try:
            expense_tracker.validate_date_range(start_date, end_date)
            break
        except ValueError as err:
            print(f"[!] {err} Please re-enter the date range.\n")

    filtered = csv_manager.filter_expenses_by_date_range_from_csv(start_date, end_date)
    display_expenses_list(filtered, f"Expenses from {start_date} to {end_date}")


def handle_financial_analytics():
    """
    Display comprehensive financial summary and analytics:
    - Overview metrics: total spending, transaction count, average expense, highest individual expense.
    - Category-wise analytics with percentages and highest-spending category.
    - Monthly expense breakdown sorted chronologically.
    """
    print("\n" + "=" * 58)
    print("         FINANCIAL SUMMARY & ANALYTICS DASHBOARD          ")
    print("=" * 58)

    records = csv_manager.read_expenses()
    if not records:
        print("  No expenses recorded yet. Add some expenses to view analytics!")
        print("=" * 58)
        return

    overview = csv_manager.get_financial_overview_from_csv()
    print(f"  Total Expenses Recorded  : ${overview['total_expenses']:.2f}")
    print(f"  Total Transactions       : {overview['transaction_count']}")
    print(f"  Average Expense          : ${overview['average_expense']:.2f}")

    highest = overview['highest_expense']
    if highest:
        print(f"  Highest Single Expense   : ${highest['amount']:.2f} on {highest['date']}")
        print(f"    Category: {highest['category']} | Description: {highest['description']}")

    # Category-wise Analytics
    print("\n--- Category-wise Analytics ---")
    cat_summary = csv_manager.get_category_summary_from_csv()
    top_cat, top_cat_amt = csv_manager.get_highest_spending_category_from_csv()

    for cat, amt in cat_summary.items():
        percentage = (amt / overview['total_expenses'] * 100) if overview['total_expenses'] > 0 else 0.0
        print(f"  {cat:<14} : ${amt:>8.2f}  ({percentage:>5.1f}%)")

    if top_cat:
        print(f"\n  [*] Highest-Spending Category : {top_cat} (${top_cat_amt:.2f})")

    # Monthly Expense Summary
    print("\n--- Monthly Expense Summary ---")
    monthly_summary = csv_manager.get_monthly_summary_from_csv()
    for month, amt in monthly_summary.items():
        print(f"  Month {month} : ${amt:>8.2f}")
    print("=" * 58)


def handle_daily_summary():
    """Prompt for a specific date and display daily total spending and transactions."""
    print("\n--- Daily Expense Summary ---")
    while True:
        date_input = safe_input("Enter date to summarize (YYYY-MM-DD): ")
        if date_input is None:
            return
        try:
            target_date = expense_tracker.validate_date(date_input)
            break
        except ValueError as err:
            print(f"[!] {err} Please try again.")

    total, count, matching = csv_manager.get_daily_summary_from_csv(target_date)
    print(f"\nSummary for {target_date}:")
    print(f"  Total Daily Spending   : ${total:.2f}")
    print(f"  Total Transactions     : {count}")

    if matching:
        print("\nItemized Daily Expenses:")
        for idx, exp in enumerate(matching, start=1):
            print(f"  {idx:>2}. {csv_manager.format_csv_expense(exp)}")
    else:
        print("  No transactions recorded on this date.")


def run_cli_loop():
    """Main interactive application loop with graceful exit handling."""
    csv_manager.initialize_csv()

    print("=" * 58)
    print("          PERSONAL EXPENSE TRACKER (CSV Persistent)       ")
    print("=" * 58)
    print(f"[i] Active persistent storage: '{csv_manager.DEFAULT_FILE}'")

    while True:
        display_menu()
        choice = safe_input("Select an option (1-9): ")
        if choice is None:
            print("\nExiting application. Goodbye!")
            break

        if choice == "1":
            handle_add_expense()
        elif choice == "2":
            handle_view_all()
        elif choice == "3":
            handle_filter_by_category()
        elif choice == "4":
            handle_search_by_description()
        elif choice == "5":
            handle_filter_by_date()
        elif choice == "6":
            handle_filter_by_date_range()
        elif choice == "7":
            handle_financial_analytics()
        elif choice == "8":
            handle_daily_summary()
        elif choice == "9":
            print("\nThank you for using Personal Expense Tracker. All data is saved in expenses.csv.")
            print("Goodbye!")
            break
        else:
            print("[!] Invalid option. Please enter a number between 1 and 9.")


def main():
    """Application entry point."""
    run_cli_loop()


if __name__ == "__main__":
    main()
