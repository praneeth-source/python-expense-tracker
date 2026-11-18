"""
csv_manager.py
--------------
Persistent CSV storage manager for the Personal Expense Tracker.

This module handles low-level file I/O operations for expenses.csv using Python's
built-in csv module. It ensures:
1. Safe persistent storage with automatic header initialization.
2. Non-destructive row appending (prevents accidental data overwriting).
3. Header duplication prevention on repeated appends.
4. Robust error handling for corrupted lines, missing files, and empty datasets.
5. High-performance, direct CSV-level filtering, search, and analytics.
6. Zero external dependencies (Python standard library only).
"""

import csv
import os

# Default CSV storage file and standard column headers
DEFAULT_FILE = "expenses.csv"
HEADERS = ["Date", "Category", "Amount", "Description"]


def get_headers():
    """
    Return a copy of the standard CSV headers.

    Returns:
        list: A list of strings representing the column headers.
    """
    return list(HEADERS)


def initialize_csv(filepath=DEFAULT_FILE):
    """
    Ensure the CSV file exists and has the correct header columns.

    If the file does not exist or is completely empty, it creates the file
    and writes the standard header row: Date, Category, Amount, Description.
    If the file already exists and has content, it leaves it untouched.

    Args:
        filepath (str): Path to the CSV file. Defaults to 'expenses.csv'.

    Returns:
        bool: True if file was newly created/initialized, False if it already existed.
    """
    try:
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        file_exists = os.path.exists(filepath)
        is_empty = False

        if file_exists:
            is_empty = os.path.getsize(filepath) == 0

        if not file_exists or is_empty:
            with open(filepath, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS)
            return True

        return False
    except OSError:
        return False


def _normalize_expense_record(expense_data):
    """
    Helper function to convert an expense dict or sequence into a normalized row:
    [Date, Category, Amount, Description].

    Args:
        expense_data (dict, list, or tuple): Raw expense record.

    Returns:
        list: Normalized [date, category, amount_str, description] row.

    Raises:
        ValueError: If sequence has fewer than 4 elements or amount is invalid.
        TypeError: If expense_data is not a dict, list, or tuple.
    """
    if isinstance(expense_data, dict):
        date_val = expense_data.get("date") or expense_data.get("Date", "")
        cat_val = expense_data.get("category") or expense_data.get("Category", "")
        amt_val = expense_data.get("amount") if "amount" in expense_data else expense_data.get("Amount", 0.0)
        desc_val = expense_data.get("description") or expense_data.get("Description", "")
    elif isinstance(expense_data, (list, tuple)):
        if len(expense_data) < 4:
            raise ValueError("Expense sequence must have at least 4 items: Date, Category, Amount, Description.")
        date_val, cat_val, amt_val, desc_val = expense_data[0], expense_data[1], expense_data[2], expense_data[3]
    else:
        raise TypeError("expense_data must be a dictionary or sequence (list/tuple).")

    try:
        float_amt = float(amt_val)
        if float_amt <= 0:
            raise ValueError("Expense amount must be greater than zero.")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount value: {amt_val}")

    return [str(date_val).strip(), str(cat_val).strip(), f"{round(float_amt, 2):.2f}", str(desc_val).strip()]


def append_expense(expense_data, filepath=DEFAULT_FILE):
    """
    Append a new expense record to the CSV file without deleting existing records.
    Automatically initializes the file with headers if missing or empty,
    and prevents duplicate headers when the file already contains data.

    Args:
        expense_data (dict, list, or tuple): Expense details to persist.
        filepath (str): Path to the CSV file. Defaults to 'expenses.csv'.

    Returns:
        dict: The saved expense record in dictionary format.
    """
    row = _normalize_expense_record(expense_data)

    file_exists = os.path.exists(filepath)
    is_empty = (not file_exists) or (os.path.getsize(filepath) == 0 if file_exists else True)

    if is_empty:
        initialize_csv(filepath)

    # Check if existing file needs a trailing newline before appending
    if file_exists and not is_empty:
        try:
            with open(filepath, mode="rb") as f:
                f.seek(-1, os.SEEK_END)
                last_char = f.read(1)
                needs_newline = last_char not in (b"\n", b"\r")
            if needs_newline:
                with open(filepath, mode="a", encoding="utf-8") as f:
                    f.write("\n")
        except OSError:
            pass

    # Append data row only (no duplicate headers)
    with open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)

    return {
        "date": row[0],
        "category": row[1],
        "amount": float(row[2]),
        "description": row[3]
    }


def append_expense_row(expense_data, filepath=DEFAULT_FILE):
    """Alias for append_expense to maintain backward compatibility."""
    return append_expense(expense_data, filepath=filepath)


def save_multiple_expenses(expenses_list, filepath=DEFAULT_FILE):
    """
    Save multiple expense records to the CSV file by appending each record.

    Args:
        expenses_list (list): List of expense dictionaries or rows.
        filepath (str): Path to the CSV file.

    Returns:
        int: Total number of records saved.
    """
    count = 0
    for item in expenses_list:
        append_expense(item, filepath=filepath)
        count += 1
    return count


def read_expenses(filepath=DEFAULT_FILE):
    """
    Read all expense records from the CSV file.
    Handles missing files, empty files, and corrupted rows gracefully.

    Corrupted rows (e.g. invalid numbers, fewer than 4 columns, empty fields)
    are skipped safely without crashing the application.

    Args:
        filepath (str): Path to the CSV file. Defaults to 'expenses.csv'.

    Returns:
        list of dict: List of valid expense dictionaries, each containing:
                      'date', 'category', 'amount', 'description'.
    """
    if not os.path.exists(filepath):
        return []

    try:
        if os.path.getsize(filepath) == 0:
            return []
    except OSError:
        return []

    records = []
    try:
        with open(filepath, mode="r", newline="", encoding="utf-8", errors="replace") as file:
            reader = csv.reader(file)
            try:
                headers = next(reader, None)
            except (StopIteration, csv.Error):
                return []

            if headers is None:
                return []

            for row in reader:
                try:
                    if not row or not any(cell.strip() for cell in row):
                        continue
                    if len(row) < 4:
                        continue

                    date_str = row[0].strip()
                    cat_str = row[1].strip()
                    amt_str = row[2].strip()
                    desc_str = row[3].strip()

                    # Require date, category, and description to be non-empty
                    if not date_str or not cat_str or not desc_str:
                        continue

                    amt_float = round(float(amt_str), 2)
                    if amt_float <= 0:
                        continue

                    records.append({
                        "date": date_str,
                        "category": cat_str,
                        "amount": amt_float,
                        "description": desc_str
                    })
                except (ValueError, IndexError, csv.Error):
                    continue
    except (OSError, csv.Error, UnicodeDecodeError):
        return []

    return records


def read_all_expenses(filepath=DEFAULT_FILE):
    """Alias for read_expenses to maintain backward compatibility."""
    return read_expenses(filepath=filepath)


def calculate_total_from_csv(filepath=DEFAULT_FILE):
    """
    Calculate the total of all expenses directly from CSV records.
    Handles missing or empty files gracefully by returning 0.0.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        float: Sum of all expense amounts rounded to 2 decimal places.
    """
    records = read_expenses(filepath=filepath)
    total = sum(rec["amount"] for rec in records)
    return round(total, 2)


def filter_expenses_by_category_from_csv(category, filepath=DEFAULT_FILE):
    """
    Filter expenses by category directly from saved CSV records.
    Matching is case-insensitive. Handles missing files gracefully.

    Args:
        category (str): Category to filter by.
        filepath (str): Path to the CSV file.

    Returns:
        list of dict: Filtered expense records.
    """
    if not isinstance(category, str) or not category.strip():
        return []

    target_category = category.strip().lower()
    records = read_expenses(filepath=filepath)
    return [rec for rec in records if rec["category"].lower() == target_category]


def search_expenses_by_description_from_csv(keyword, filepath=DEFAULT_FILE):
    """
    Search expenses by keyword in description directly from CSV records.
    Case-insensitive substring search. Handles missing files gracefully.

    Args:
        keyword (str): Text to search for in descriptions.
        filepath (str): Path to the CSV file.

    Returns:
        list of dict: Matching expense records.
    """
    if not isinstance(keyword, str) or not keyword.strip():
        return []

    search_term = keyword.strip().lower()
    records = read_expenses(filepath=filepath)
    return [rec for rec in records if search_term in rec["description"].lower()]


def filter_expenses_by_date_from_csv(target_date, filepath=DEFAULT_FILE):
    """
    Filter expenses matching an exact date (YYYY-MM-DD) directly from CSV records.
    Handles missing files gracefully.

    Args:
        target_date (str): Date string to match.
        filepath (str): Path to the CSV file.

    Returns:
        list of dict: Matching expense records.
    """
    if not isinstance(target_date, str) or not target_date.strip():
        return []

    date_str = target_date.strip()
    records = read_expenses(filepath=filepath)
    return [rec for rec in records if rec["date"] == date_str]


def filter_expenses_by_date_range_from_csv(start_date, end_date, filepath=DEFAULT_FILE):
    """
    Filter expenses within an inclusive date range [start_date, end_date] directly from CSV records.
    Handles missing files gracefully.

    Args:
        start_date (str): Start date string (YYYY-MM-DD).
        end_date (str): End date string (YYYY-MM-DD).
        filepath (str): Path to the CSV file.

    Returns:
        list of dict: Expense records falling within the range.
    """
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        return []

    start = start_date.strip()
    end = end_date.strip()
    records = read_expenses(filepath=filepath)
    return [rec for rec in records if start <= rec["date"] <= end]


def calculate_filtered_total(filtered_records):
    """
    Calculate the total spending sum for any list of expense records.

    Args:
        filtered_records (list): List of expense dictionaries.

    Returns:
        float: Sum of amounts rounded to 2 decimal places.
    """
    if not filtered_records:
        return 0.0
    return round(sum(rec["amount"] for rec in filtered_records), 2)


def format_csv_expense(expense):
    """
    Format a saved expense dictionary into a clean, human-readable string.

    Args:
        expense (dict): Expense dictionary containing date, category, amount, description.

    Returns:
        str: Formatted display string.
    """
    return (
        f"Date: {expense['date']} | "
        f"Category: {expense['category']:<13} | "
        f"Amount: ${expense['amount']:>8.2f} | "
        f"Description: {expense['description']}"
    )


def get_monthly_summary_from_csv(filepath=DEFAULT_FILE):
    """
    Calculate total expenses for each month directly from CSV records.
    Handles missing or empty files gracefully.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        dict: Mapping of 'YYYY-MM' strings to total spending rounded to 2 decimal places.
    """
    records = read_expenses(filepath=filepath)
    monthly_totals = {}
    for rec in records:
        month = rec["date"][:7]
        monthly_totals[month] = monthly_totals.get(month, 0.0) + rec["amount"]

    return {k: round(monthly_totals[k], 2) for k in sorted(monthly_totals.keys())}


def get_category_summary_from_csv(filepath=DEFAULT_FILE):
    """
    Calculate spending for each category directly from CSV records.
    Handles missing or empty files gracefully.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        dict: Mapping of category names to total spending rounded to 2 decimal places.
    """
    records = read_expenses(filepath=filepath)
    category_totals = {}
    for rec in records:
        cat = rec["category"]
        category_totals[cat] = category_totals.get(cat, 0.0) + rec["amount"]

    return {k: round(category_totals[k], 2) for k in sorted(category_totals.keys())}


def get_highest_spending_category_from_csv(filepath=DEFAULT_FILE):
    """
    Identify the highest-spending category directly from CSV records.
    Handles missing or empty files gracefully.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        tuple: (category_name, total_amount) or (None, 0.0) if no records.
    """
    summary = get_category_summary_from_csv(filepath=filepath)
    if not summary:
        return (None, 0.0)

    top_cat = max(summary.items(), key=lambda pair: pair[1])
    return (top_cat[0], top_cat[1])


def get_daily_summary_from_csv(target_date, filepath=DEFAULT_FILE):
    """
    Calculate total expenses and matching records for a selected date directly from CSV.
    Handles missing or empty files gracefully.

    Args:
        target_date (str): Target date (YYYY-MM-DD).
        filepath (str): Path to the CSV file.

    Returns:
        tuple: (total_amount, count, matching_records)
    """
    records = read_expenses(filepath=filepath)
    matching = [rec for rec in records if rec["date"] == target_date.strip()]
    total = sum(rec["amount"] for rec in matching)
    return (round(total, 2), len(matching), matching)


def get_highest_expense_from_csv(filepath=DEFAULT_FILE):
    """
    Identify and return the single largest individual expense from CSV records.
    Handles missing or empty files gracefully.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        dict or None: Highest expense record or None if no records exist.
    """
    records = read_expenses(filepath=filepath)
    if not records:
        return None

    return max(records, key=lambda rec: rec["amount"])


def get_average_expense_from_csv(filepath=DEFAULT_FILE):
    """
    Calculate the average spending per recorded transaction directly from CSV records.
    Handles missing or empty files gracefully by returning 0.0.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        float: Average spending amount rounded to 2 decimal places, or 0.0 if empty.
    """
    records = read_expenses(filepath=filepath)
    if not records:
        return 0.0

    total = sum(rec["amount"] for rec in records)
    return round(total / len(records), 2)


def get_financial_overview_from_csv(filepath=DEFAULT_FILE):
    """
    Compile complete financial overview metrics from CSV records:
    - Total expenses
    - Total number of transactions
    - Average expense
    - Highest expense

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        dict: Complete financial overview metrics.
    """
    records = read_expenses(filepath=filepath)
    count = len(records)
    total = round(sum(rec["amount"] for rec in records), 2)
    avg = round(total / count, 2) if count > 0 else 0.0
    highest = get_highest_expense_from_csv(filepath=filepath)

    return {
        "total_expenses": total,
        "transaction_count": count,
        "average_expense": avg,
        "highest_expense": highest
    }
