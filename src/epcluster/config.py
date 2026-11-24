"""Central configuration and naming conventions.

All randomness is seeded so that every figure and membership table in this
repository is byte-for-byte reproducible.
"""
from __future__ import annotations

RANDOM_STATE: int = 42          # locked seed for K-Means initialisation
N_INIT: int = 100               # K-Means restarts (local-minimum protection)
K_RANGE: tuple[int, ...] = (2, 3, 4, 5, 6)   # candidate k for the silhouette sweep

# Adopted solutions (documented decisions, see README "Methods"):
K_STATIC_2025: int = 2          # highest silhouette on the static layer (S ~ 0.61)
K_TRAJECTORY: int = 2           # policy-level binary split (mainstream vs anomaly);
                                # note: unconstrained silhouette argmax gives k = 4.

S_MIN: float = 0.25             # C2: minimum within-cluster silhouette
N_MIN: int = 2                  # C1: no singleton clusters
LABEL_THRESHOLD: float = 0.5    # |z| threshold for High/Low qualitative labels

# Analysis layers: name -> (column triple used for clustering)
LAYERS: dict[str, tuple[str, str, str]] = {
    "static_2025": ("ep_2025", "ur_2025", "cdd_2025"),
    "static_2050": ("ep_2050", "ur_2050", "cdd_2050"),
    "trajectory":  ("d_ep", "d_ur", "d_cdd"),
}

CLUSTER_COLORS: dict[int, str] = {0: "#4C72B0", 1: "#C44E52",
                                  2: "#55A868", 3: "#DD8452"}
DPI: int = 300