import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def create_income_expense_chart(filtered_df):
    """Create income vs expenses chart."""
    if not filtered_df.empty:
        monthly_data = filtered_df.copy()
        monthly_data["month_year"] = monthly_data["date"].dt.strftime("%Y-%m")
        monthly_summary = (
            monthly_data.groupby(["month_year", "type"])["amount"]
            .sum()
            .unstack()
            .fillna(0)
        )

        if "income" not in monthly_summary.columns:
            monthly_summary["income"] = 0
        if "expense" not in monthly_summary.columns:
            monthly_summary["expense"] = 0

        monthly_summary["balance"] = (
            monthly_summary["income"] - monthly_summary["expense"]
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=monthly_summary.index,
                y=monthly_summary["income"],
                name="Income",
                marker_color="green",
            )
        )
        fig.add_trace(
            go.Bar(
                x=monthly_summary.index,
                y=monthly_summary["expense"],
                name="Expenses",
                marker_color="red",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=monthly_summary.index,
                y=monthly_summary["balance"],
                name="Balance",
                line=dict(color="blue", width=2),
            )
        )

        fig.update_layout(
            barmode="group",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend_title="Type",
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected time period")


def create_expense_category_chart(filtered_df):
    """Create expense categories pie chart."""
    if not filtered_df.empty and "expense" in filtered_df["type"].values:
        expense_df = filtered_df[filtered_df["type"] == "expense"]
        expense_by_category = (
            expense_df.groupby("category")["amount"].sum().reset_index()
        )

        fig = px.pie(
            expense_by_category,
            values="amount",
            names="category",
            title="Expense Distribution by Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for the selected time period")


def create_balance_trend_chart(filtered_df):
    """Create balance trend chart."""
    if not filtered_df.empty:
        # Create daily balance data
        filtered_df = filtered_df.sort_values("date")
        daily_data = filtered_df.copy()
        daily_data["amount_signed"] = np.where(
            daily_data["type"] == "expense", -daily_data["amount"], daily_data["amount"]
        )
        daily_data = daily_data.groupby("date")["amount_signed"].sum().reset_index()
        daily_data["cumulative_balance"] = daily_data["amount_signed"].cumsum()

        fig = px.line(
            daily_data,
            x="date",
            y="cumulative_balance",
            title="Balance Over Time",
            markers=True,
        )

        fig.update_traces(line=dict(color="royalblue", width=2))
        fig.update_layout(xaxis_title="Date", yaxis_title="Balance ($)", height=400)

        # Add a horizontal line at y=0
        fig.add_shape(
            type="line",
            x0=daily_data["date"].min(),
            y0=0,
            x1=daily_data["date"].max(),
            y1=0,
            line=dict(color="red", width=1, dash="dash"),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected time period")
