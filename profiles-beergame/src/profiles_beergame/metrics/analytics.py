from __future__ import annotations

from typing import Dict, Any

import pandas as pd
import numpy as np


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
    """Per-role aggregate KPIs."""
    agg = df.groupby("role").agg(
        avg_inventory=("inventory", "mean"),
        avg_backlog=("backlog", "mean"),
        total_holding_cost=("cost_holding", "sum"),
        total_backlog_cost=("cost_backlog", "sum"),
        avg_holding_cost=("cost_holding", "mean"),
        avg_backlog_cost=("cost_backlog", "mean"),
        order_variance=("placed_order", "var"),
        order_mean=("placed_order", "mean"),
    ).reset_index()
    agg["total_cost"] = agg["total_holding_cost"] + agg["total_backlog_cost"]
    return agg


def compute_service_level(df: pd.DataFrame) -> pd.DataFrame:
    """Compute fill-rate service level per role.

    Fill rate = periods with zero backlog / total periods.
    """
    def _fill_rate(sub: pd.DataFrame) -> float:
        return (sub["backlog"] == 0).mean()

    sl = df.groupby("role").apply(_fill_rate, include_groups=False).reset_index(name="fill_rate")
    return sl


def compute_order_oscillation(df: pd.DataFrame) -> pd.DataFrame:
    """Order oscillation index: fraction of periods where order direction reverses."""
    results = []
    for role in df["role"].unique():
        orders = df[df["role"] == role]["placed_order"].values
        if len(orders) < 3:
            results.append({"role": role, "oscillation_index": 0.0})
            continue
        diffs = np.diff(orders)
        sign_changes = np.sum(diffs[:-1] * diffs[1:] < 0)
        results.append({
            "role": role,
            "oscillation_index": sign_changes / max(1, len(diffs) - 1),
        })
    return pd.DataFrame(results)


def compute_system_cost(df: pd.DataFrame) -> float:
    """Total cost across all roles and all periods."""
    return float(df["cost_holding"].sum() + df["cost_backlog"].sum())


def compare_scenarios(
    results: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compare KPIs across multiple named scenarios.

    Args:
        results: mapping of scenario_name -> simulation DataFrame

    Returns:
        Wide DataFrame with one row per scenario, columns for key metrics.
    """
    rows = []
    for name, df in results.items():
        bw = compute_bullwhip(df)
        kpis = summarize_kpis(df)
        sl = compute_service_level(df)
        row: Dict[str, Any] = {"scenario": name}
        row["system_total_cost"] = compute_system_cost(df)
        row["avg_bullwhip"] = bw["bullwhip_factor"].mean()
        row["max_bullwhip"] = bw["bullwhip_factor"].max()
        row["avg_fill_rate"] = sl["fill_rate"].mean()
        row["avg_inventory"] = kpis["avg_inventory"].mean()
        row["avg_backlog"] = kpis["avg_backlog"].mean()
        rows.append(row)
    return pd.DataFrame(rows)


