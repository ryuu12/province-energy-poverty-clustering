"""Publication-style figures: silhouette sweep, hull scatter, trajectory grid."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from . import config
from .clustering import SweepResult, convex_hull


def _save(fig, path: str | Path | None) -> None:
    if path is not None:
        fig.savefig(path, dpi=config.DPI, bbox_inches="tight")
    plt.close(fig)


def silhouette_sweep_figure(results: dict[int, SweepResult], chosen_k: int,
                            path: str | Path | None = None) -> None:
    """S(k) curve with Kaufman-Rousseeuw interpretation bands."""
    ks = sorted(results)
    scores = [results[k].score for k in ks]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.axhspan(0.51, 0.70, color="#fff3cd", alpha=.35, label="Reasonable")
    ax.axhspan(0.26, 0.50, color="#cce5ff", alpha=.35, label="Weak but real")
    ax.plot(ks, scores, marker="o", lw=2.5, color="#1f4e79")
    for k, s in zip(ks, scores):
        ax.annotate(f"{s:.3f}", (k, s), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=9, fontweight="bold")
    ax.scatter([chosen_k], [results[chosen_k].score], s=220, color="red",
               edgecolor="black", zorder=5, label=f"adopted k = {chosen_k}")
    ax.set_xlabel("number of clusters k", fontweight="bold")
    ax.set_ylabel("average silhouette S(k)", fontweight="bold")
    ax.set_title("Silhouette sweep (trajectory layer, deltas)")
    ax.set_xticks(ks)
    ax.grid(alpha=.4, ls=":")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    _save(fig, path)


def hull_scatter_figure(df: pd.DataFrame, x: str, y: str, size: str,
                        label_col: str, names: dict[int, str],
                        annotate: list[str] | None = None,
                        title: str = "", path: str | Path | None = None) -> None:
    """Bubble scatter (size = third delta) with convex-hull cluster boundaries."""
    fig, ax = plt.subplots(figsize=(11, 8))
    dmax = df[size].max()
    for c in sorted(df[label_col].unique()):
        sub = df[df[label_col] == c]
        col = config.CLUSTER_COLORS[int(c)]
        ax.scatter(sub[x], sub[y], s=sub[size] / dmax * 1500 + 100, c=col,
                   edgecolor="black", lw=1.2, alpha=.75, zorder=4,
                   label=names[int(c)])
        hull = convex_hull(sub[[x, y]].to_numpy())
        ax.plot(hull[:, 0], hull[:, 1], color=col, lw=2, zorder=3)
        ax.fill(hull[:, 0], hull[:, 1], color=col, alpha=.10, zorder=1)
        ax.annotate(names[int(c)], (sub[x].mean(), sub[y].mean()), ha="center",
                    fontsize=9, fontweight="bold", color=col, zorder=6,
                    bbox=dict(boxstyle="round,pad=.25", fc="white", ec=col, alpha=.9))
    if annotate:
        for _, r in df[df.province.isin(annotate)].iterrows():
            ax.annotate(r.province, (r[x], r[y]), textcoords="offset points",
                        xytext=(0, 12), ha="center", fontsize=8.5, fontweight="bold")
    ax.axhline(0, color="red", ls="--", lw=1.1, alpha=.8)
    ax.text(.01, .015, f"{y} = 0 reference", transform=ax.transAxes,
            fontsize=8.5, color="red")
    ax.set_xlabel(x, fontweight="bold")
    ax.set_ylabel(y, fontweight="bold")
    ax.set_title(title or f"Cluster hulls: {x} vs {y}")
    ax.grid(alpha=.35)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=9)
    fig.tight_layout()
    _save(fig, path)


def trajectory_grid_figure(df: pd.DataFrame, label_col: str,
                           x_vars: tuple[str, ...] = ("ur", "cdd"),
                           names: dict[int, str] | None = None,
                           path: str | Path | None = None) -> None:
    """Rows = clusters, cols = variables; arrows show 2025 -> 2050 per province,
    thick lines show the cluster mean and median trajectories."""
    clusters = sorted(df[label_col].unique())
    fig, axes = plt.subplots(len(clusters), len(x_vars),
                             figsize=(6.2 * len(x_vars), 5.2 * len(clusters)),
                             squeeze=False)
    for row, c in enumerate(clusters):
        sub = df[df[label_col] == c]
        col = config.CLUSTER_COLORS[int(c)]
        for colj, v in enumerate(x_vars):
            ax = axes[row][colj]
            ax.scatter(df[f"{v}_2025"], df["ep_2025"], color="lightgray",
                       s=45, alpha=.6, zorder=1)
            for _, r in sub.iterrows():
                ax.annotate("", xy=(r[f"{v}_2050"], r["ep_2050"]),
                            xytext=(r[f"{v}_2025"], r["ep_2025"]),
                            arrowprops=dict(arrowstyle="->", color=col,
                                            lw=1.4, alpha=.65), zorder=2)
            ax.scatter(sub[f"{v}_2025"], sub["ep_2025"], s=55, c=col,
                       edgecolor="black", lw=.8, zorder=3)
            ax.scatter(sub[f"{v}_2050"], sub["ep_2050"], s=80, c=col,
                       marker="D", edgecolor="black", lw=.8, zorder=4)
            for agg, mk in (("mean", "*"), ("median", "X")):
                p25 = sub[[f"{v}_2025", "ep_2025"]].agg(agg).to_numpy()
                p50 = sub[[f"{v}_2050", "ep_2050"]].agg(agg).to_numpy()
                ax.plot([p25[0], p50[0]], [p25[1], p50[1]],
                        color="black" if mk == "*" else "darkred",
                        ls="-" if mk == "*" else "--", lw=2.6, zorder=5)
                ax.scatter([p50[0]], [p50[1]], marker=mk, s=260 if mk == "*" else 160,
                           color="gold" if mk == "*" else "darkred",
                           edgecolor="black", zorder=6)
            if colj == 0:
                ax.set_ylabel((names or {}).get(int(c), f"cluster {c}")
                              + "\nEP (kWh)", fontweight="bold", fontsize=10)
            if row == 0:
                ax.set_title(f"{v.upper()} 2025→2050", fontweight="bold")
            ax.axhline(0, color="red", ls=":", lw=1, alpha=.6)
            ax.grid(alpha=.4, ls="--")
    handles = [Line2D([0], [0], marker="*", color="w", markerfacecolor="gold",
                      markeredgecolor="k", markersize=13, label="mean trajectory"),
               Line2D([0], [0], marker="X", color="w", markerfacecolor="darkred",
                      markeredgecolor="k", markersize=11, label="median trajectory"),
               Line2D([0], [0], color="k", lw=1.6, label="province shift 25→50")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=10)
    fig.tight_layout(rect=[0, .03, 1, 1])
    _save(fig, path)