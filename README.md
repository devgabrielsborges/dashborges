# DashBorges

A personal finance dashboard application for monitoring and visualizing financial data.

## Overview

DashBorges is a powerful financial dashboard tool built with Python that allows users to track, analyze, and visualize personal financial data. Built with Streamlit and FastAPI, it provides an intuitive interface for financial management and reporting.

## Features

- **Interactive Financial Visualizations**: Create charts and graphs to visualize income, expenses, and balance trends
- **Transaction Management**: Add, view, and analyze financial transactions
- **Data Import/Export**: Import transactions from CSV files and view summarized financial data
- **Filtering Options**: Filter transactions by date, category, and type
- **Financial Summary**: Get quick insights with financial summary metrics
- **API Integration**: Full backend API built with FastAPI for data management
- **Responsive Design**: Optimized for desktop and mobile viewing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dashborges.git

# Navigate to the project directory
cd dashborges

# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Start the application
python main.py
```

## Usage

### Running the Dashboard

1. After starting the application, the FastAPI backend will be running at `http://127.0.0.1:8000`
2. To run the Streamlit dashboard, execute:
   ```bash
   streamlit run src/dashborges/dashborges.py
   ```

### Managing Transactions

Transactions can be added in several ways:
1. Manually through the sidebar form
2. By uploading a CSV file with transaction data
3. Using the "Load Sample Data" button for demonstration purposes

### Financial Analytics

The dashboard provides several visualizations:
- Income vs. Expenses charts
- Expense Categories breakdown
- Balance Trends over time

### API Usage

```python
# Example: Using the API client to fetch transactions
from dashborges.api_client import DashBorgesClient

client = DashBorgesClient()
transactions = client.get_transactions(
    start_date="2025-01-01",
    end_date="2025-02-01",
    category="Food",
    type="expense"
)
```

## Configuration

The SQLite database is stored in the `data` directory by default:

```python
DATABASE_URL = "sqlite:///home/borges/development/dashborges/data/finances.db"
```

## API Reference

### Transactions

- `GET /transactions/`: List all transactions with optional filters
- `GET /transactions/{id}`: Get a specific transaction
- `POST /transactions/`: Create a new transaction
- `PUT /transactions/{id}`: Update a transaction
- `DELETE /transactions/{id}`: Delete a transaction
- `POST /transactions/bulk/`: Upload multiple transactions

### Summary

- `GET /summary/`: Get financial summary with optional date range filters

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers at support@dashborges.com.
