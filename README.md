# Personal Expense Tracker with CSV

A beginner-friendly, resilient, and modular command-line application built entirely with Python standard libraries to track, search, filter, and analyze personal expenses persistently using CSV storage.

---

## Project Overview

Managing daily expenses is essential for financial awareness. The **Personal Expense Tracker** provides a complete, robust command-line solution to record daily expenses, categorize transactions, filter by dates or categories, search by keywords, and view comprehensive financial analytics—all stored persistently in a human-readable CSV format (`expenses.csv`).

---

## Key Features

1. **Daily Expense Recording & Persistence**:
   - Records transactions with **Amount**, **Category**, **Description**, and **Date**.
   - Persists data permanently in `expenses.csv` using Python's built-in `csv` module.
   - Automatically writes headers on initialization and prevents duplicate headers on repeated appends.

2. **Strict & Beginner-Friendly Input Validation**:
   - **Amounts**: Rejects negative numbers, zero, boolean values, and non-numeric characters; automatically rounds to 2 decimal places.
   - **Categories**: Validates against 7 standard categories (case-insensitive):
     - `Food`, `Transport`, `Education`, `Shopping`, `Entertainment`, `Healthcare`, `Other`.
   - **Descriptions**: Rejects empty strings or whitespace-only descriptions.
   - **Dates**: Strictly validates `YYYY-MM-DD` calendar dates (including leap years like `2024-02-29`) and allows pressing Enter to default to today's date.
   - **Date Ranges**: Enforces that start dates cannot be after end dates.

3. **Multi-Criteria Search & Filtering**:
   - **Category Filtering**: Filter expenses by any supported category.
   - **Description Search**: Fast, case-insensitive substring searching across descriptions.
   - **Specific Date Filtering**: Filter all expenses recorded on a selected date.
   - **Date Range Filtering**: Inclusive chronological date range filtering (`start_date <= date <= end_date`).
   - **Filtered Total Display**: Every filter and search view automatically computes and displays total spending and transaction counts for matching results.

4. **Financial Summary & Analytics Dashboard**:
   - **Overall Metrics**: Total expenses, total transactions, average spending per transaction, and highest individual expense.
   - **Category-wise Breakdown**: Spending amounts and percentage distribution per category, highlighting the top-spending category.
   - **Monthly Summary**: Chronologically sorted total spending grouped by month (`YYYY-MM`).
   - **Daily Expense Summary**: Itemized breakdown and total spending for any chosen calendar date.

5. **Data Safety & Error Resilience**:
   - **Corrupted File Tolerance**: Safely skips broken, malformed, or non-numeric rows in `expenses.csv` without crashing.
   - **Missing & Empty File Handling**: Gracefully returns empty sets or `$0.00` totals if the CSV is missing or empty.
   - **Graceful Interruptions**: Intercepts `Ctrl+C` (`KeyboardInterrupt`) and `EOFError` safely at any input prompt to prevent abrupt terminal tracebacks.

---

## Project Structure

```text
personal expense tracker/
│
├── main.py                     # CLI coordinator, menu presentation & interactive loops
├── expense_tracker.py          # Business logic, data validation & in-memory analytics
├── csv_manager.py              # Low-level CSV persistence layer & direct file queries
├── expenses.csv                # Persistent CSV storage file (standard UTF-8)
├── README.md                   # Complete documentation, user guide & architecture
├── .gitignore                  # Git untracked patterns (bytecode, virtual environments)
└── tests/                      # Automated test suite (Python built-in unittest)
    ├── __init__.py             # Test package identifier
    ├── test_csv_manager.py     # Unit tests for CSV operations & persistence (17 tests)
    ├── test_expense_tracker.py # Unit tests for validation, business logic & analytics (47 tests)
    └── test_edge_cases.py      # Hardening tests for corrupted files & boundary conditions (8 tests)
```

---

## Purpose of Every File

| File / Folder | Purpose & Architecture Role |
| :--- | :--- |
| **[`main.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/main.py)** | Main entry point for the user interface. Presents formatted menus, handles input validation loops with `safe_input`, and connects user actions to business and storage logic. |
| **[`expense_tracker.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/expense_tracker.py)** | Business logic service layer. Contains functions for input validation, expense creation, category management, filtering, searching, and financial calculations. |
| **[`csv_manager.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/csv_manager.py)** | Storage abstraction layer. Manages persistent file operations on `expenses.csv`, ensures correct header initialization, handles safe row appending, and provides direct CSV queries. |
| **[`expenses.csv`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/expenses.csv)** | Persistent database file in standard comma-separated format (`Date,Category,Amount,Description`). Preserves data across sessions. |
| **[`tests/test_csv_manager.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/tests/test_csv_manager.py)** | Automated tests for CSV file creation, idempotency, header protection, reading, and writing. |
| **[`tests/test_expense_tracker.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/tests/test_expense_tracker.py)** | Automated tests for amount/date/category validations, filtering, searching, monthly summaries, and averages. |
| **[`tests/test_edge_cases.py`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/tests/test_edge_cases.py)** | Automated tests verifying resilience against corrupted CSV rows, missing newlines, high-precision amounts, and edge conditions. |
| **[`README.md`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/README.md)** | Comprehensive project documentation. |
| **[`.gitignore`](file:///c:/Users/parim/Downloads/personal%20expense%20tracker/.gitignore)** | Prevents Python bytecode (`__pycache__`), virtual environments, and IDE configs from being tracked. |

---

## Technical Constraints & Design Principles

- **Standard Library Only**: Built strictly with Python 3 standard libraries (`csv`, `os`, `sys`, `datetime`, `unittest`, `tempfile`). No third-party packages or `pip install` commands required.
- **Modular Architecture**: Clean separation between presentation (`main.py`), business rules (`expense_tracker.py`), and storage (`csv_manager.py`).
- **Beginner-Friendly Syntax**: Clear, readable code with descriptive variable names, docstrings, and comprehensive inline comments.
- **Data Hardening**: Never overwrites existing expense records accidentally.

---

## How to Run the Application

### Prerequisites
- Python 3.8 or higher installed.

### 1. Launch the Application
```bash
python main.py
```

### 2. Run the Automated Test Suite
Run all 72 automated unit tests across the test suite:
```bash
python -m unittest discover tests -v
```

---

## Example Usage Walkthrough

### 1. Main Menu
```text
==========================================================
           PERSONAL EXPENSE TRACKER - MAIN MENU           
==========================================================
  1. Add New Expense
  2. View All Saved Expenses
  3. Filter Expenses by Category
  4. Search Expenses by Description
  5. Filter Expenses by Specific Date
  6. Filter Expenses by Date Range
  7. Financial Summary & Analytics Dashboard
  8. Daily Expense Summary
  9. Exit Application
----------------------------------------------------------
```

### 2. Adding an Expense
```text
--- Add New Expense ---
Enter expense amount ($): 28.50
Supported categories: Food, Transport, Education, Shopping, Entertainment, Healthcare, Other
Enter category: food
Enter description: Dinner with friends
Enter date (YYYY-MM-DD) [press Enter for today]: 2026-11-18

[SUCCESS] Expense recorded and saved to expenses.csv:
  Date: 2026-11-18 | Category: Food          | Amount: $   28.50 | Description: Dinner with friends
```

### 3. Financial Summary & Analytics Dashboard
```text
==========================================================
         FINANCIAL SUMMARY & ANALYTICS DASHBOARD          
==========================================================
  Total Expenses Recorded  : $78.50
  Total Transactions       : 3
  Average Expense          : $26.17
  Highest Single Expense   : $35.00 on 2026-11-20
    Category: Education | Description: Python Course

--- Category-wise Analytics ---
  Education      : $   35.00  ( 44.6%)
  Food           : $   28.50  ( 36.3%)
  Transport      : $   15.00  ( 19.1%)

  [*] Highest-Spending Category : Education ($35.00)

--- Monthly Expense Summary ---
  Month 2026-11 : $   78.50
==========================================================
```

---

## Development Roadmap (All 6 Phases Completed)

- [x] **Phase 1: Project Setup** – Establish modular directory structure, entry point, initial storage verification, tests, and documentation.
- [x] **Phase 2: Expense Recording** – Implement in-memory expense tracking, 7 supported categories, data validation, totals, and category filtering.
- [x] **Phase 3: CSV Persistence and Expense Management** – Persistent storage in `expenses.csv`, header preservation, idempotency, and application restart resilience.
- [x] **Phase 4: Expense Filtering, Search and Input Validation** – Category filters, description substring search, date filters, date range queries, and while-loop validation.
- [x] **Phase 5: Financial Summary & Analytics** – Monthly summaries, category breakdown, highest/average expense calculations, and analytics dashboard.
- [x] **Phase 6: Final Polish, Packaging & Edge-Case Hardening** – Corrupted CSV handling, safe Ctrl+C input handling, packaging preparation, and complete edge-case test suite.
