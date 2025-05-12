# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-05-11

### Highlights

- Initial release featuring interactive financial visualizations, comprehensive transaction management, and a robust backend.

### Added

- Interactive Plotly visualizations for income vs. expenses, category breakdowns, and balance trends.
- Transaction interface supporting add, view, import/export CSV, and detailed filtering.
- Dynamic sidebar filters for date ranges, categories, and transaction types.
- Key financial metrics dashboard displaying total income, total expenses, and net balance.
- FastAPI backend exposing RESTful CRUD endpoints for transactions and summary data.
- Responsive Streamlit UI optimized for both desktop and mobile devices.

### Changed

- Modular project architecture divided into API client, data handler, database, and UI components.
- Configured Poetry for streamlined dependency management and build processes.

### Fixed

- No bug fixes in this initial release.

### Removed

- None

## [0.2.0] - 2025-05-12

### Highlights for 0.2.0

- Enhanced financial visualizations and data handling capabilities.

### Added in 0.2.0

- **Visualizations**:
  - `create_income_expense_chart`: Generates income vs. expenses charts for better financial insights.
  - `create_expense_category_chart`: Visualizes expense breakdown by category.
  - `create_balance_trend_chart`: Displays balance trends over time.
- **Utilities**:
  - `calculate_summary`: Computes total income, expenses, and balance.
  - `filter_data_by_time`: Filters transaction data by specified time periods.
- **UI Components**:
  - `create_sidebar`: Introduces a sidebar for streamlined data management.
  - `display_financial_summary`: Summarizes key financial metrics.
  - `display_transaction_table`: Displays a detailed transaction table.
- **Data Handling**:
  - `load_csv_data`: Enables CSV data import for transactions.
  - `add_transaction`, `update_transaction`, `delete_transaction`: CRUD operations for transaction management.
