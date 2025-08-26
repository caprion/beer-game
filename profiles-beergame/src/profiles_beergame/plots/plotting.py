from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt


def plot_time_series(df: pd.DataFrame) -> None:
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
    plt.show()


