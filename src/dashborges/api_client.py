import requests
import pandas as pd
from datetime import datetime, date
import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashBorgesClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.is_api_available = self._check_api_available()

        # Local storage for offline mode
        self.data_dir = Path(os.path.expanduser("~")) / ".dashborges"
        self.data_file = self.data_dir / "local_transactions.json"

        # Create local storage directory if it doesn't exist
        if not self.is_api_available:
            self._ensure_local_storage()

    def _check_api_available(self):
        """Check if the API is available."""
        try:
            response = requests.get(f"{self.base_url}/transactions/", timeout=1)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            logger.warning("API server is not available. Running in offline mode.")
            return False

    def _ensure_local_storage(self):
        """Ensure local storage directory and file exist."""
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)

        # Create empty transactions file if it doesn't exist
        if not self.data_file.exists():
            with open(self.data_file, "w") as f:
                json.dump([], f)

    def _load_local_transactions(self):
        """Load transactions from local storage."""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading local transactions: {e}")
            return []

    def _save_local_transactions(self, transactions):
        """Save transactions to local storage."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(transactions, f, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving local transactions: {e}")
            return False

    def get_transactions(
        self, start_date=None, end_date=None, category=None, type=None
    ):
        """Fetch transactions from API with optional filters."""
        # Try to use API if available
        if self.is_api_available:
            try:
                params = {}
                if start_date:
                    params["start_date"] = (
                        start_date.isoformat()
                        if isinstance(start_date, date)
                        else start_date
                    )
                if end_date:
                    params["end_date"] = (
                        end_date.isoformat() if isinstance(end_date, date) else end_date
                    )
                if category:
                    params["category"] = category
                if type:
                    params["type"] = type

                response = requests.get(f"{self.base_url}/transactions/", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df = pd.DataFrame(data)
                        df["date"] = pd.to_datetime(df["date"])
                        return df
                    return pd.DataFrame(
                        {
                            "date": [],
                            "category": [],
                            "description": [],
                            "amount": [],
                            "type": [],
                        }
                    )
            except requests.exceptions.RequestException:
                self.is_api_available = False
                logger.warning("API connection failed. Switching to offline mode.")

        # Fallback to local storage
        transactions = self._load_local_transactions()
        df = (
            pd.DataFrame(transactions)
            if transactions
            else pd.DataFrame(
                {
                    "date": [],
                    "category": [],
                    "description": [],
                    "amount": [],
                    "type": [],
                }
            )
        )

        # Apply filters if data exists
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            if start_date:
                start_date = pd.to_datetime(start_date)
                df = df[df["date"] >= start_date]
            if end_date:
                end_date = pd.to_datetime(end_date)
                df = df[df["date"] <= end_date]
            if category:
                df = df[df["category"] == category]
            if type:
                df = df[df["type"] == type.lower()]

        return df

    def add_transaction(self, date_val, category, description, amount, trans_type):
        """Add a single transaction."""
        if isinstance(date_val, datetime) or isinstance(date_val, date):
            date_val = date_val.isoformat()

        transaction = {
            "date": date_val,
            "category": category,
            "description": description,
            "amount": float(amount),
            "type": trans_type.lower(),
        }

        # Try API if available
        if self.is_api_available:
            try:
                response = requests.post(
                    f"{self.base_url}/transactions/", json=transaction
                )
                api_success = response.status_code == 200 or response.status_code == 201
                if api_success:
                    return True
                else:
                    self.is_api_available = False
                    logger.warning("API request failed. Switching to offline mode.")
            except requests.exceptions.RequestException:
                self.is_api_available = False
                logger.warning("API connection failed. Switching to offline mode.")

        # Fallback to local storage
        transactions = self._load_local_transactions()

        # Add ID for local transactions
        transaction["id"] = len(transactions) + 1 if transactions else 1
        transactions.append(transaction)

        return self._save_local_transactions(transactions)

    def bulk_upload_transactions(self, df):
        """Upload multiple transactions from a DataFrame."""
        if df.empty:
            return False

        # Convert DataFrame to list of dicts
        transactions = []
        for _, row in df.iterrows():
            transactions.append(
                {
                    "date": row["date"].isoformat()
                    if isinstance(row["date"], (datetime, date))
                    else row["date"],
                    "category": row["category"],
                    "description": row["description"],
                    "amount": float(row["amount"]),
                    "type": row["type"].lower(),
                }
            )

        # Try API if available
        if self.is_api_available:
            try:
                response = requests.post(
                    f"{self.base_url}/transactions/bulk/", json=transactions
                )
                api_success = response.status_code == 200 or response.status_code == 201
                if api_success:
                    return True
                else:
                    self.is_api_available = False
                    logger.warning("API request failed. Switching to offline mode.")
            except requests.exceptions.RequestException:
                self.is_api_available = False
                logger.warning("API connection failed. Switching to offline mode.")

        # Fallback to local storage
        existing_transactions = self._load_local_transactions()
        next_id = len(existing_transactions) + 1 if existing_transactions else 1

        for transaction in transactions:
            transaction["id"] = next_id
            next_id += 1
            existing_transactions.append(transaction)

        return self._save_local_transactions(existing_transactions)

    def get_summary(self, start_date=None, end_date=None):
        """Get financial summary for a time period."""
        # Try API if available
        if self.is_api_available:
            try:
                params = {}
                if start_date:
                    params["start_date"] = (
                        start_date.isoformat()
                        if isinstance(start_date, date)
                        else start_date
                    )
                if end_date:
                    params["end_date"] = (
                        end_date.isoformat() if isinstance(end_date, date) else end_date
                    )

                response = requests.get(f"{self.base_url}/summary/", params=params)
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException:
                self.is_api_available = False
                logger.warning("API connection failed. Switching to offline mode.")

        # Fallback: calculate summary from local data
        df = self.get_transactions(start_date, end_date)

        if df.empty:
            return {
                "total_income": 0,
                "total_expenses": 0,
                "balance": 0,
                "period": "No data",
            }

        total_income = df[df["type"] == "income"]["amount"].sum()
        total_expenses = df[df["type"] == "expense"]["amount"].sum()
        balance = total_income - total_expenses

        period = "All time"
        if start_date and end_date:
            period = f"{start_date} to {end_date}"
        elif start_date:
            period = f"Since {start_date}"
        elif end_date:
            period = f"Until {end_date}"

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "period": period,
        }
