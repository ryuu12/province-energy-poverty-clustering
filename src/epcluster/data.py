"""Loading and derivation of the province-level panel."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

REQUIRED = ["province", "ep_2025", "ep_2050", "ur_2025", "ur_2050",
            "cdd_2025", "cdd_2050"]


def load_panel(path: str | Path = "data/province_panel.csv") -> pd.DataFrame:
    """Read the province panel and derive the trajectory (delta) columns.

    Delta convention (documented in data/DATA_NOTE.md):
        d_ep  = ep_2025 - ep_2050   (positive  -> gap NARROWS / improves)
        d_ur  = ur_2050 - ur_2025   (percentage points)
        d_cdd = cdd_2050 - cdd_2025 (climate shock, degree-days)
    """
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"columns missing from panel: {missing}")
    if df[REQUIRED[1:]].isna().any().any():
        raise ValueError("panel contains NaN values; clean the source CSV first")

    df = df.copy()
    df["d_ep"] = df["ep_2025"] - df["ep_2050"]
    df["d_ur"] = df["ur_2050"] - df["ur_2025"]
    df["d_cdd"] = df["cdd_2050"] - df["cdd_2025"]
    return df


def layer_matrix(df: pd.DataFrame, layer: str) -> pd.DataFrame:
    """Return the (n x 3) numeric matrix of a named analysis layer."""
    cols = config.LAYERS[layer]
    return df[list(cols)]