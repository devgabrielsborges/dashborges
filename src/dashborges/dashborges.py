import streamlit as st
from datetime import datetime
import calendar
import pandas as pd
import sys
import argparse

from data_handler import (
    load_csv_data,
    add_transaction,
    generate_sample_data,
    get_api_status,
    set_api_port,
)
from ui_components import (
    create_sidebar,
    display_financial_summary,
    display_transaction_table,
)
from visualizations import (
    create_income_expense_chart,
    create_expense_category_chart,
    create_balance_trend_chart,
)
from utils import calculate_summary, filter_data_by_time

# Parse command-line arguments for API port
parser = argparse.ArgumentParser()
parser.add_argument("--api_port", type=int, default=8000, help="API server port")

# Handle the case when Streamlit adds its own arguments
if len(sys.argv) > 1:
    # Get only our arguments after the -- separator
    our_args = []
    for i, arg in enumerate(sys.argv):
        if arg == "--" and i + 1 < len(sys.argv):
            our_args = sys.argv[i + 1 :]
            break

    if our_args:
        args, _ = parser.parse_known_args(our_args)
        # Configure API client with the specified port
        api_port = args.api_port
        print(f"Using API port: {api_port}")
        set_api_port(api_port)

# Set page configuration
st.set_page_config(
    page_title="DashBorges - Personal Finance Dashboard", page_icon="💰", layout="wide"
)

# Application title and description
st.title("💰 DashBorges - Personal Finance Dashboard")
st.markdown("Track and analyze your personal finances with ease!")

# Check API status and display banner if offline
api_available = get_api_status()
if not api_available:
    st.warning("""
        ⚠️ Running in offline mode. API server is not available.
        To use the full features, run the API server with: `python main.py`
        Your data will be stored locally and can be synchronized when the API is available.
    """)

# Initialize session state for data storage
if "transactions" not in st.session_state:
    # Import client to load existing transactions
    from api_client import DashBorgesClient

    # Initialize client and fetch transactions
    client = DashBorgesClient()
    st.session_state["transactions"] = client.get_transactions()

    # Add debug info showing that data was loaded
    st.sidebar.info(
        f"Loaded {len(st.session_state['transactions'])} transactions on startup"
    )

    # If no transactions were found, initialize with empty DataFrame
    if (
        st.session_state["transactions"] is None
        or st.session_state["transactions"].empty
    ):
        st.session_state["transactions"] = pd.DataFrame(
            {
                "date": [],
                "category": [],
                "description": [],
                "amount": [],
                "type": [],  # 'income' or 'expense'
            }
        )

# Create sidebar for data input/upload
create_sidebar()

# Main dashboard
if (
    st.session_state.get("transactions") is not None
    and not st.session_state["transactions"].empty
):
    # Time period filter
    col1, col2, col3 = st.columns(3)
    with col1:
        time_filter = st.selectbox(
            "Time Period", ["All Time", "This Month", "This Year"]
        )

    # Filter data based on time period selection
    filtered_df, period_name = filter_data_by_time(
        st.session_state["transactions"], time_filter
    )

    # Calculate summary statistics
    total_income, total_expenses, balance = calculate_summary(filtered_df)

    # Display financial summary metrics
    display_financial_summary(period_name, total_income, total_expenses, balance)

    # Row for charts
    st.subheader("Financial Analytics")
    col1, col2 = st.columns(2)

    # Income vs Expenses chart
    with col1:
        st.write("Income vs Expenses")
        create_income_expense_chart(filtered_df)

    # Expense categories chart
    with col2:
        st.write("Expense Categories")
        create_expense_category_chart(filtered_df)

    # Balance over time trend
    st.subheader("Balance Trends")
    create_balance_trend_chart(filtered_df)

    # Transactions table
    display_transaction_table(filtered_df)

else:
    st.info(
        "No transactions data available. Please add transactions using the sidebar."
    )

    # Sample data for demonstration
    if st.button("Load Sample Data"):
        st.session_state["transactions"] = generate_sample_data()

# Footer
st.markdown("---")
st.caption("DashBorges - Personal Finance Dashboard | Created with Streamlit")

# Add API status indicator in the footer
api_status = "🟢 Connected" if api_available else "🔴 Offline"
st.sidebar.markdown(f"API Status: {api_status}")
