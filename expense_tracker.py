"""
expense_tracker.py
------------------
Business logic and in-memory expense tracking module for the Personal Expense Tracker.

This module provides core expense management functions:
1. Strict data validation:
   - Expense amounts (rejects negative numbers, zero, booleans, non-numeric values).
   - Supported categories (Food, Transport, Education, Shopping, Entertainment, Healthcare, Other).
   - Non-empty descriptions.
   - Valid calendar dates in YYYY-MM-DD format.
   - Valid chronological date ranges (start_date <= end_date).
2. Expense management operations:
   - Adding daily expenses (with optional CSV persistence).
   - Viewing and formatting expense records.
   - Substring searching in descriptions (case-insensitive).
   - Multi-criteria filtering (category, specific date, date range).
   - Financial analytics (monthly summaries, category totals, top-spending category,
     daily summaries, highest expense, average spending, complete overview).
3. Zero external dependencies (Python standard library only).
"""

from datetime import datetime, date

# Standard supported categories across the application
CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Other"
]

# Internal in-memory storage for active session tracking
_expenses = []


def get_categories():
    """
    Return a copy of the list of supported expense categories.

    Returns:
        list: Supported category names.
    """
    return list(CATEGORIES)


def get_default_categories():
    """
    Alias for get_categories() to maintain backward compatibility.

    Returns:
        list: Supported category names.
    """
    return get_categories()


def validate_amount(amount):
    """
    Validate and convert an expense amount.

    The amount must be a positive number (> 0).

    Args:
        amount (int, float, or str): The amount to validate.

    Returns:
        float: The validated amount rounded to 2 decimal places.

    Raises:
        ValueError: If amount is non-numeric, boolean, or <= 0.
    """
    if isinstance(amount, bool):
        raise ValueError("Amount must be a valid positive number.")

    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid positive number.")

    if numeric_amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")

    return round(numeric_amount, 2)


def validate_category(category):
    """
    Validate and normalize the expense category against supported categories.
    Matching is case-insensitive and returns the standard capitalized category.

    Args:
        category (str): The category name.

    Returns:
        str: The normalized canonical category name.

    Raises:
        ValueError: If the category is empty or not recognized.
    """
    if not isinstance(category, str) or not category.strip():
        allowed = ", ".join(CATEGORIES)
        raise ValueError(f"Category cannot be empty. Supported categories: {allowed}")

    cleaned = category.strip().lower()
    for supported in CATEGORIES:
        if supported.lower() == cleaned:
            return supported

    allowed = ", ".join(CATEGORIES)
    raise ValueError(f"Invalid category '{category}'. Supported categories: {allowed}")


def validate_description(description):
    """
    Validate that an expense description is a non-empty string.

    Args:
        description (str): Description text.

    Returns:
        str: Cleaned description string.

    Raises:
        ValueError: If description is empty or whitespace only.
    """
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Description cannot be empty.")

    return description.strip()


def validate_date(date_str):
    """
    Validate that a date string follows the 'YYYY-MM-DD' format and is a valid calendar date.

    Args:
        date_str (str): Date in 'YYYY-MM-DD' format.

    Returns:
        str: Validated date string.

    Raises:
        ValueError: If format is invalid or date does not exist.
    """
    if not isinstance(date_str, str) or not date_str.strip():
        raise ValueError("Date cannot be empty. Please use YYYY-MM-DD format (e.g. 2026-11-18).")

    cleaned = date_str.strip()
    try:
        parsed = datetime.strptime(cleaned, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format '{date_str}'. Please use YYYY-MM-DD format (e.g. 2026-11-18).")


def validate_date_range(start_date_str, end_date_str):
    """
    Validate that both start and end date strings are valid YYYY-MM-DD calendar dates,
    and that start_date <= end_date.

    Args:
        start_date_str (str): Beginning of date range (YYYY-MM-DD).
        end_date_str (str): End of date range (YYYY-MM-DD).

    Returns:
        tuple: (valid_start_date, valid_end_date) as YYYY-MM-DD strings.

    Raises:
        ValueError: If dates are invalid or start_date is after end_date.
    """
    valid_start = validate_date(start_date_str)
    valid_end = validate_date(end_date_str)

    if valid_start > valid_end:
        raise ValueError(f"Start date ({valid_start}) cannot be after end date ({valid_end}).")

    return valid_start, valid_end


def add_expense(amount, category, description, date_str=None, expenses_list=None, save_to_csv=False, csv_filepath=None):
    """
    Add a daily expense record with amount, category, description, and date.

    If date_str is omitted or None, the current system date is used.
    If save_to_csv is True, the expense is also permanently appended to the CSV file.

    Args:
        amount (int, float, or str): The cost of the expense.
        category (str): The category (e.g. Food, Transport, etc.).
        description (str): Brief detail about the purchase.
        date_str (str, optional): Date in 'YYYY-MM-DD'. Defaults to today.
        expenses_list (list, optional): Target list to store expense into. Defaults to module list.
        save_to_csv (bool, optional): If True, appends to CSV file. Defaults to False.
        csv_filepath (str, optional): Destination CSV file path. Defaults to csv_manager.DEFAULT_FILE.

    Returns:
        dict: The created expense record dictionary.
    """
    valid_amount = validate_amount(amount)
    valid_category = validate_category(category)
    valid_description = validate_description(description)

    if date_str is None or (isinstance(date_str, str) and not date_str.strip()):
        valid_date = date.today().strftime("%Y-%m-%d")
    else:
        valid_date = validate_date(date_str)

    expense = {
        "amount": valid_amount,
        "category": valid_category,
        "description": valid_description,
        "date": valid_date
    }

    target_list = _expenses if expenses_list is None else expenses_list
    target_list.append(expense)

    if save_to_csv:
        import csv_manager
        target_csv = csv_filepath or csv_manager.DEFAULT_FILE
        csv_manager.append_expense(expense, filepath=target_csv)

    return expense


def load_from_csv(filepath=None):
    """
    Load expenses from the CSV storage file into the in-memory tracker list.

    Args:
        filepath (str, optional): Path to the CSV file. Defaults to csv_manager.DEFAULT_FILE.

    Returns:
        list: The updated in-memory expense list.
    """
    global _expenses
    import csv_manager
    target_csv = filepath or csv_manager.DEFAULT_FILE
    records = csv_manager.read_expenses(filepath=target_csv)
    _expenses = list(records)
    return list(_expenses)


def save_to_csv(filepath=None):
    """
    Save all current in-memory expenses to the CSV storage file.

    Args:
        filepath (str, optional): Path to the CSV file. Defaults to csv_manager.DEFAULT_FILE.

    Returns:
        int: Total number of records saved.
    """
    import csv_manager
    target_csv = filepath or csv_manager.DEFAULT_FILE
    return csv_manager.save_multiple_expenses(_expenses, filepath=target_csv)


def get_all_expenses(expenses_list=None):
    """
    Retrieve all recorded expenses.

    Args:
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        list: A copy of all recorded expense dictionaries.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    return list(target_list)


def calculate_total_expenses(expenses_list=None):
    """
    Calculate the total sum of all recorded expenses.

    Args:
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        float: Total amount of all expenses, rounded to 2 decimal places.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    total = sum(item["amount"] for item in target_list)
    return round(total, 2)


def filter_expenses_by_category(category, expenses_list=None):
    """
    Filter expenses by a specific category (case-insensitive).

    Args:
        category (str): Category name to filter by.
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        list: Expenses matching the specified category.
    """
    normalized_category = validate_category(category)
    target_list = _expenses if expenses_list is None else expenses_list
    return [item for item in target_list if item["category"] == normalized_category]


def search_expenses_by_description(keyword, expenses_list=None):
    """
    Search expenses by keyword substring in description (case-insensitive).

    Args:
        keyword (str): Search term.
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        list: Matching expense dictionaries.

    Raises:
        ValueError: If keyword is empty or whitespace only.
    """
    if not isinstance(keyword, str) or not keyword.strip():
        raise ValueError("Search keyword cannot be empty.")

    search_term = keyword.strip().lower()
    target_list = _expenses if expenses_list is None else expenses_list
    return [item for item in target_list if search_term in item["description"].lower()]


def filter_expenses_by_date(target_date, expenses_list=None):
    """
    Filter expenses that match a specific date (YYYY-MM-DD).

    Args:
        target_date (str): Date string to match.
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        list: Matching expense dictionaries.

    Raises:
        ValueError: If target_date is not a valid YYYY-MM-DD date.
    """
    valid_date = validate_date(target_date)
    target_list = _expenses if expenses_list is None else expenses_list
    return [item for item in target_list if item["date"] == valid_date]


def filter_expenses_by_date_range(start_date, end_date, expenses_list=None):
    """
    Filter expenses that fall within an inclusive date range [start_date, end_date].

    Args:
        start_date (str): Beginning date (YYYY-MM-DD).
        end_date (str): Ending date (YYYY-MM-DD).
        expenses_list (list, optional): Source list. Defaults to module list.

    Returns:
        list: Matching expense dictionaries.

    Raises:
        ValueError: If dates are invalid or start_date is after end_date.
    """
    valid_start, valid_end = validate_date_range(start_date, end_date)
    target_list = _expenses if expenses_list is None else expenses_list
    return [item for item in target_list if valid_start <= item["date"] <= valid_end]


def clear_expenses(expenses_list=None):
    """
    Clear all recorded expenses from memory (useful for testing or resetting).

    Args:
        expenses_list (list, optional): Target list to clear. Defaults to module list.
    """
    global _expenses
    if expenses_list is None:
        _expenses.clear()
    else:
        expenses_list.clear()


def format_expense(expense):
    """
    Format a single expense dictionary into a user-friendly readable line.

    Args:
        expense (dict): Expense dictionary containing date, category, amount, description.

    Returns:
        str: Formatted text line.
    """
    return (
        f"Date: {expense['date']} | "
        f"Category: {expense['category']:<13} | "
        f"Amount: ${expense['amount']:>8.2f} | "
        f"Description: {expense['description']}"
    )


# --- Financial Summary & Analytics ---

def calculate_monthly_summary(expenses_list=None):
    """
    Calculate total expenses grouped by month (YYYY-MM).

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        dict: Mapping of 'YYYY-MM' strings to total spending rounded to 2 decimal places,
              sorted chronologically by month.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    monthly_totals = {}
    for item in target_list:
        month_key = item["date"][:7]  # Extracts 'YYYY-MM'
        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + item["amount"]

    return {k: round(monthly_totals[k], 2) for k in sorted(monthly_totals.keys())}


def calculate_category_summary(expenses_list=None):
    """
    Calculate total spending for each category that has recorded expenses.

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        dict: Mapping of category names to total spending rounded to 2 decimal places.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    category_totals = {}
    for item in target_list:
        cat = item["category"]
        category_totals[cat] = category_totals.get(cat, 0.0) + item["amount"]

    return {k: round(category_totals[k], 2) for k in sorted(category_totals.keys())}


def get_highest_spending_category(expenses_list=None):
    """
    Identify the category with the highest total spending.

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        tuple: (category_name, total_amount) or (None, 0.0) if no expenses exist.
    """
    summary = calculate_category_summary(expenses_list=expenses_list)
    if not summary:
        return (None, 0.0)

    top_cat = max(summary.items(), key=lambda pair: pair[1])
    return (top_cat[0], top_cat[1])


def calculate_daily_summary(target_date, expenses_list=None):
    """
    Calculate total expenses for a selected date (YYYY-MM-DD).

    Args:
        target_date (str): Date string to calculate summary for.
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        tuple: (total_amount, count, matching_expenses)
    """
    valid_date = validate_date(target_date)
    target_list = _expenses if expenses_list is None else expenses_list
    matching = [item for item in target_list if item["date"] == valid_date]
    total = sum(item["amount"] for item in matching)
    return (round(total, 2), len(matching), matching)


def get_highest_expense(expenses_list=None):
    """
    Identify the largest individual expense transaction.

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        dict or None: The expense record dictionary with maximum amount, or None if empty.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    if not target_list:
        return None

    return max(target_list, key=lambda item: item["amount"])


def calculate_average_expense(expenses_list=None):
    """
    Calculate average spending per recorded transaction.

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        float: Average expense amount rounded to 2 decimal places, or 0.0 if empty.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    if not target_list:
        return 0.0

    total = sum(item["amount"] for item in target_list)
    return round(total / len(target_list), 2)


def get_financial_overview(expenses_list=None):
    """
    Compile a complete financial overview dictionary:
    - Total expenses
    - Total number of transactions
    - Average expense
    - Highest expense

    Args:
        expenses_list (list, optional): Source list of expenses. Defaults to module list.

    Returns:
        dict: Complete financial overview.
    """
    target_list = _expenses if expenses_list is None else expenses_list
    count = len(target_list)
    total = round(sum(item["amount"] for item in target_list), 2)
    avg = round(total / count, 2) if count > 0 else 0.0
    highest = get_highest_expense(expenses_list=target_list)

    return {
        "total_expenses": total,
        "transaction_count": count,
        "average_expense": avg,
        "highest_expense": highest
    }
