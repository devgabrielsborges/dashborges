import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from api_client import DashBorgesClient

# Create client instance
client = DashBorgesClient()


def get_api_status():
    """Check if the API is available."""
    return client.is_api_available


def load_csv_data(uploaded_file):
    """Load transaction data from a CSV file."""
    try:
        data = pd.read_csv(uploaded_file)
        required_columns = ["date", "category", "description", "amount", "type"]

        if all(col in data.columns for col in required_columns):
            data["date"] = pd.to_datetime(data["date"])

            # Upload to API
            success = client.bulk_upload_transactions(data)

            if success:
                # Fetch all transactions to update the state
                st.session_state["transactions"] = client.get_transactions()
                return True, "Data uploaded successfully!"
            else:
                return False, "Failed to upload data."
        else:
            return (
                False,
                "CSV must contain columns: date, category, description, amount, type",
            )
    except Exception as e:
        return False, f"Error: {e}"


def add_transaction(date, category, description, amount, trans_type):
    """Add a new transaction to the dataset."""
    # Add transaction via API
    success = client.add_transaction(date, category, description, amount, trans_type)

    if success:
        # Refresh transactions in session state
        st.session_state["transactions"] = client.get_transactions()
        return True
    return False


def generate_sample_data():
    """Generate sample transaction data and upload to API."""
    # Generate sample data
    np.random.seed(42)

    # Generate dates for the past 6 months
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(months=6)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # Categories
    income_categories = ["Salary", "Investments", "Gifts", "Other Income"]
    expense_categories = [
        "Housing",
        "Food",
        "Transportation",
        "Utilities",
        "Entertainment",
        "Healthcare",
        "Shopping",
        "Other Expenses",
    ]

    # Generate sample transactions
    sample_data = []

    # Income transactions
    for _ in range(30):
        date = np.random.choice(dates)
        category = np.random.choice(income_categories)

        if category == "Salary":
            amount = np.random.uniform(2000, 5000)
            desc = "Monthly Salary"
        elif category == "Investments":
            amount = np.random.uniform(100, 1000)
            desc = np.random.choice(["Dividend", "Interest", "Stock Sale"])
        else:
            amount = np.random.uniform(50, 500)
            desc = f"{category} - Sample"

        sample_data.append(
            {
                "date": date,
                "category": category,
                "description": desc,
                "amount": round(amount, 2),
                "type": "income",
            }
        )

    # Expense transactions
    for _ in range(150):
        date = np.random.choice(dates)
        category = np.random.choice(expense_categories)

        if category == "Housing":
            amount = np.random.uniform(800, 1500)
            desc = np.random.choice(["Rent", "Mortgage", "Property Tax"])
        elif category == "Food":
            amount = np.random.uniform(10, 100)
            desc = np.random.choice(["Grocery", "Restaurant", "Coffee Shop"])
        else:
            amount = np.random.uniform(10, 200)
            desc = f"{category} - Sample"

        sample_data.append(
            {
                "date": date,
                "category": category,
                "description": desc,
                "amount": round(amount, 2),
                "type": "expense",
            }
        )

    sample_df = pd.DataFrame(sample_data)

    # Upload sample data
    client.bulk_upload_transactions(sample_df)

    # Return data
    return client.get_transactions()


def get_transactions(
    start_date=None, end_date=None, category=None, transaction_type=None
):
    """Get transactions with optional filters."""
    return client.get_transactions(start_date, end_date, category, transaction_type)
