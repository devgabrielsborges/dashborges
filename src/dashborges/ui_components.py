import streamlit as st
import pandas as pd
from datetime import datetime
from data_handler import (
    load_csv_data,
    add_transaction,
    update_transaction,
    delete_transaction,
)


def create_sidebar():
    """Create the sidebar UI for data management."""
    with st.sidebar:
        st.header("Data Management")

        # File uploader for CSV data
        uploaded_file = st.file_uploader("Upload transaction data (CSV)", type=["csv"])
        if uploaded_file is not None:
            success, message = load_csv_data(uploaded_file)
            if success:
                st.success(message)
            else:
                st.error(message)

        # Manual transaction entry
        st.subheader("Add New Transaction")
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", datetime.now())
                category = st.selectbox(
                    "Category",
                    [
                        "Salary",
                        "Investments",
                        "Gifts",
                        "Other Income",
                        "Housing",
                        "Food",
                        "Transportation",
                        "Utilities",
                        "Entertainment",
                        "Healthcare",
                        "Shopping",
                        "Other Expenses",
                    ],
                )
            with col2:
                description = st.text_input("Description")
                amount = st.number_input("Amount", min_value=0.0, step=0.01)
                trans_type = st.radio("Type", ["Income", "Expense"], horizontal=True)

            submit_button = st.form_submit_button("Add Transaction")
            if submit_button:
                if add_transaction(
                    date, category, description, amount, trans_type.lower()
                ):
                    st.success("Transaction added successfully!")


def display_financial_summary(period_name, total_income, total_expenses, balance):
    """Display financial summary metrics."""
    st.subheader(f"Financial Summary ({period_name})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income:,.2f}", "")
    col2.metric("Total Expenses", f"${total_expenses:,.2f}", "")
    col3.metric(
        "Balance",
        f"${balance:,.2f}",
        f"{balance / total_income * 100:.1f}%" if total_income > 0 else "0%",
    )


def display_transaction_table(filtered_df):
    """Display transaction table with edit and delete capabilities."""
    st.subheader("Recent Transactions")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Recent Transactions", "All Transactions"])

    # Check if we have transactions to display
    if filtered_df.empty:
        st.info("No transactions available for the selected time period.")
        return

    # Ensure transactions have an ID column
    if "id" not in filtered_df.columns:
        filtered_df = filtered_df.reset_index().rename(columns={"index": "id"})

    # Sort by date, most recent first
    display_df = filtered_df.sort_values("date", ascending=False)

    with tab1:
        # Show only the 10 most recent transactions (recent view prefix)
        _display_interactive_table(display_df.head(10), key_prefix="recent")

    with tab2:
        # Show all transactions (all view prefix)
        _display_interactive_table(display_df, key_prefix="all")

    # Show edit form once in sidebar if editing
    if "edit_transaction" in st.session_state:
        _display_edit_form(st.session_state["edit_transaction"])


def _display_interactive_table(df, key_prefix=""):
    """Display an interactive transaction table with edit and delete buttons."""
    # Create a unique key for each transaction row
    for idx, (i, row) in enumerate(df.iterrows()):
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 2, 1, 0.5, 0.5])

            # Format date for display
            date_str = (
                row["date"].strftime("%Y-%m-%d")
                if hasattr(row["date"], "strftime")
                else row["date"]
            )

            # Display transaction info
            col1.write(date_str)
            col2.write(row["category"])
            col3.write(row["description"])

            # Format amount and use appropriate color based on transaction type
            amount_text = f"${row['amount']:.2f}"
            color = "#008000" if row["type"] == "income" else "#FF0000"
            col4.markdown(
                f"<span style='color:{color}'>{amount_text}</span>",
                unsafe_allow_html=True,
            )

            # Build unique keys using prefix and row ID to avoid duplicates across tables
            # key_prefix differentiates between recent and all views
            prefix = f"{key_prefix}_" if key_prefix else ""
            edit_key = f"{prefix}edit_{i}"
            delete_key = f"{prefix}delete_{i}"

            # Edit button with unique key
            if col5.button("✏️", key=edit_key):
                st.session_state["edit_transaction"] = row.to_dict()

            # Delete button with unique key
            if col6.button("🗑️", key=delete_key):
                if delete_transaction(row["id"]):
                    st.success("Transaction deleted successfully!")
                else:
                    st.error("Failed to delete transaction.")

        # Add a light separator between rows
        st.markdown(
            "<hr style='margin: 0; padding: 0; height: 1px'>", unsafe_allow_html=True
        )


def _display_edit_form(transaction):
    """Display form for editing a transaction."""
    st.sidebar.header("Edit Transaction")

    with st.sidebar.form("edit_transaction_form"):
        # Format date for the date input
        if isinstance(transaction["date"], str):
            try:
                date_val = datetime.strptime(transaction["date"], "%Y-%m-%d").date()
            except ValueError:
                date_val = datetime.now().date()
        else:
            date_val = (
                transaction["date"]
                if hasattr(transaction["date"], "date")
                else datetime.now().date()
            )

        # Create the form fields
        date = st.date_input("Date", value=date_val)

        category = st.selectbox(
            "Category",
            [
                "Salary",
                "Investments",
                "Gifts",
                "Other Income",
                "Housing",
                "Food",
                "Transportation",
                "Utilities",
                "Entertainment",
                "Healthcare",
                "Shopping",
                "Other Expenses",
            ],
            index=[
                "Salary",
                "Investments",
                "Gifts",
                "Other Income",
                "Housing",
                "Food",
                "Transportation",
                "Utilities",
                "Entertainment",
                "Healthcare",
                "Shopping",
                "Other Expenses",
            ].index(transaction["category"])
            if transaction["category"]
            in [
                "Salary",
                "Investments",
                "Gifts",
                "Other Income",
                "Housing",
                "Food",
                "Transportation",
                "Utilities",
                "Entertainment",
                "Healthcare",
                "Shopping",
                "Other Expenses",
            ]
            else 0,
        )

        description = st.text_input("Description", value=transaction["description"])
        amount = st.number_input(
            "Amount", min_value=0.0, step=0.01, value=float(transaction["amount"])
        )

        trans_type = st.radio(
            "Type",
            ["Income", "Expense"],
            index=0 if transaction["type"].lower() == "income" else 1,
            horizontal=True,
        )

        col1, col2 = st.columns(2)

        # Submit button
        submit = col1.form_submit_button("Update")
        if submit:
            if update_transaction(
                transaction["id"],
                date,
                category,
                description,
                amount,
                trans_type.lower(),
            ):
                st.success("Transaction updated successfully!")
                # Clear the edit state and refresh
                del st.session_state["edit_transaction"]
            else:
                st.error("Failed to update transaction.")

        # Cancel button
        cancel = col2.form_submit_button("Cancel")
        if cancel:
            del st.session_state["edit_transaction"]
