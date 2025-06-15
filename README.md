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
- **Persistent Storage**: All data is safely stored in Docker volumes with automatic backups

## Installation

### Standard Installation

*Ensure you have [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) and Python installed*

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

### Docker Installation (Recommended)

You can run DashBorges using Docker, which provides complete data persistence and easy management:

```bash
# Clone the repository
git clone https://github.com/yourusername/dashborges.git

# Navigate to the project directory
cd dashborges

# Build and start the container using Docker Compose
docker-compose up -d

# Access the dashboard at http://localhost:8501
# Access the API at http://localhost:8000
```

**Data Persistence**: All application data (database, configuration, logs) persists between container restarts and updates in dedicated Docker volumes:
- `dashborges_data`: Stores the SQLite database and user data
- `dashborges_config`: Stores configuration files
- `dashborges_logs`: Stores application logs

### Docker Management Script

A comprehensive helper script is provided to manage Docker operations and data:

```bash
# Make the script executable (first time only)
chmod +x docker-manage.sh

# Start the application
./docker-manage.sh start

# View logs
./docker-manage.sh logs

# Stop the application
./docker-manage.sh stop

# Create comprehensive backup (includes all data, config, and logs)
./docker-manage.sh backup

# Restore from backup
./docker-manage.sh restore ./backups/dashborges_full_backup_20250615_120000.tar.gz

# View volume information
./docker-manage.sh volumes

# Clean up everything (WARNING: Destroys all data)
./docker-manage.sh clean
```

Run `./docker-manage.sh` without arguments to see all available commands.

## Data Management

### Backup and Restore

**Automatic Backups**: The application automatically creates backups of critical data during operations.

**Manual Backups**: Create comprehensive backups using the management script:
```bash
./docker-manage.sh backup
```

**Restore Data**: Restore from any backup file:
```bash
./docker-manage.sh restore <backup_file>
```

### Storage Locations

When running in Docker:
- **Database**: `/app/data/finances.db`
- **Local storage**: `/app/data/local_transactions.json`
- **Backups**: `/app/data/backups/`
- **Configuration**: `/app/config/`
- **Logs**: `/app/logs/`

All these directories are mounted as Docker volumes for persistence.

## Usage

### Running the Dashboard

1. After starting the application, the FastAPI backend will be running at `http://127.0.0.1:8000`
2. To run the Streamlit dashboard, execute:
   ```bash
   poetry run streamlit run src/dashborges/dashborges.py
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

### Environment Variables

The application supports the following environment variables for container deployment:

- `DASHBORGES_DATA_DIR`: Directory for data storage (default: `/app/data`)
- `DASHBORGES_CONFIG_DIR`: Directory for configuration files (default: `/app/config`)
- `DASHBORGES_LOGS_DIR`: Directory for log files (default: `/app/logs`)

### Database Configuration

The SQLite database location is automatically configured based on the data directory:

```python
# Database location is configurable via environment
DATA_DIR = os.environ.get("DASHBORGES_DATA_DIR", "/app/data")
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'finances.db')}"
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
