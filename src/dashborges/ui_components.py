import streamlit as st
from datetime import datetime
from data_handler import load_csv_data, add_transaction


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
    """Display transaction table."""
    st.subheader("Recent Transactions")
    st.dataframe(
        filtered_df.sort_values("date", ascending=False)
        .head(10)
        .style.format({"amount": "${:.2f}"})
        .apply(
            lambda x: [
                "background-color: #008000"
                if x.type == "income"
                else "background-color: #FF0000"
                for i in x
            ],
            axis=1,
        )
    )

    if st.button("View All Transactions"):
        st.dataframe(
            filtered_df.sort_values("date", ascending=False)
            .style.format({"amount": "${:.2f}"})
            .apply(
                lambda x: [
                    "background-color: #008000"
                    if x.type == "income"
                    else "background-color: #FF0000"
                    for i in x
                ],
                axis=1,
            )
        )
