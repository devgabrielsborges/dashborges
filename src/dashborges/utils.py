from datetime import datetime
import calendar
import pandas as pd


def calculate_summary(df):
    """Calculate financial summary statistics."""
    if df.empty:
        return 0, 0, 0

    total_income = df[df["type"] == "income"]["amount"].sum()
    total_expenses = df[df["type"] == "expense"]["amount"].sum()
    balance = total_income - total_expenses

    return total_income, total_expenses, balance


def filter_data_by_time(df, time_filter):
    """Filter transaction data by time period."""
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    if time_filter == "This Month":
        current_month = datetime.now().month
        current_year = datetime.now().year
        filtered_df = df[
            (df["date"].dt.month == current_month)
            & (df["date"].dt.year == current_year)
        ]
        period_name = f"{calendar.month_name[current_month]} {current_year}"
    elif time_filter == "This Year":
        current_year = datetime.now().year
        filtered_df = df[df["date"].dt.year == current_year]
        period_name = f"{current_year}"
    else:
        filtered_df = df
        period_name = "All Time"

    return filtered_df, period_name
