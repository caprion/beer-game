from __future__ import annotations

from typing import Optional

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_time_series(df: pd.DataFrame, show: bool = False) -> Figure:
    """Plot order, inventory and backlog time-series for each role.

    Returns the matplotlib Figure so callers (Streamlit, tests, exports)
    can use it without side-effects.  Set *show=True* for interactive use.
    """
    roles = df["role"].unique()
    fig, axes = plt.subplots(len(roles), 1, figsize=(10, 2.2 * len(roles)), sharex=True)
    if len(roles) == 1:
        axes = [axes]
    for ax, role in zip(axes, roles):
        sub = df[df["role"] == role]
        ax.plot(sub["t"], sub["placed_order"], label="orders")
        ax.plot(sub["t"], sub["inventory"], label="inventory")
        ax.plot(sub["t"], sub["backlog"], label="backlog")
        ax.set_title(role)
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("period")
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def plot_bullwhip(bullwhip_df: pd.DataFrame, show: bool = False) -> Figure:
    """Bar chart of bullwhip factors by role."""
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#e74c3c" if v > 1.5 else "#f39c12" if v > 1.0 else "#2ecc71"
              for v in bullwhip_df["bullwhip_factor"]]
    ax.bar(bullwhip_df["role"], bullwhip_df["bullwhip_factor"], color=colors)
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, label="No amplification")
    ax.set_ylabel("Bullwhip Factor")
    ax.set_title("Demand Amplification by Role")
    ax.legend()
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def plot_costs(df: pd.DataFrame, show: bool = False) -> Figure:
    """Stacked cost waterfall: holding vs backlog per role."""
    costs = df.groupby("role").agg(
        holding=("cost_holding", "sum"),
        backlog=("cost_backlog", "sum"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(costs["role"], costs["holding"], label="Holding cost", color="#3498db")
    ax.bar(costs["role"], costs["backlog"], bottom=costs["holding"],
           label="Backlog cost", color="#e74c3c")
    ax.set_ylabel("Total Cost")
    ax.set_title("Cost Breakdown by Role")
    ax.legend()
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def plot_order_comparison(df: pd.DataFrame, show: bool = False) -> Figure:
    """Overlay all roles' placed orders on one chart to visualize amplification."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for role in df["role"].unique():
        sub = df[df["role"] == role]
        ax.plot(sub["t"], sub["placed_order"], label=role, linewidth=1.5)
    ax.set_xlabel("Period")
    ax.set_ylabel("Order Quantity")
    ax.set_title("Order Amplification Across Supply Chain")
    ax.legend()
    plt.tight_layout()
    if show:
        plt.show()
    return fig


