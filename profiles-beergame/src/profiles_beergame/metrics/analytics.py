from __future__ import annotations

import pandas as pd


def compute_bullwhip(df: pd.DataFrame) -> pd.DataFrame:
    """Compute bullwhip factor per role as var(placed_order)/var(retailer demand).

    Assumes df has columns: ['t','role','placed_order','incoming_order']
    Retailer demand taken as retailer's incoming_order.
    """
    demand = df[df["role"] == "retailer"]["incoming_order"].var(ddof=1)
    if demand == 0 or pd.isna(demand):
        demand = 1.0
    out = (
        df.groupby("role")["placed_order"].var(ddof=1).fillna(0.0) / demand
    ).reset_index(name="bullwhip_factor")
    return out


def summarize_kpis(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("role").agg(
        avg_inventory=("inventory", "mean"),
        avg_backlog=("backlog", "mean"),
        avg_holding_cost=("cost_holding", "mean"),
        avg_backlog_cost=("cost_backlog", "mean"),
        order_variance=("placed_order", "var"),
    ).reset_index()
    return agg


