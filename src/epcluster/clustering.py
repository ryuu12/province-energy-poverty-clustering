"""K-Means clustering with silhouette-based k selection and screening rules.

Pipeline (see README "Methods"):
  1. z-score standardisation per layer (units are incommensurable);
  2. K-Means (k-means++ seeding, R restarts) for every candidate k;
  3. silhouette sweep S(k);
  4. statistical screening C1 (no singletons), C2 (min cluster silhouette),
     plus a manual/theoretical admissibility check C4 applied by the analyst;
  5. k* = argmax S(k) among admissible candidates (overridable by policy).
"""
from __future__ import annotations

import dataclasses

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

from . import config


@dataclasses.dataclass
class SweepResult:
    """Outcome of one candidate k."""
    k: int
    labels: np.ndarray
    score: float                 # global silhouette S(k)
    sizes: tuple[int, ...]
    cluster_silhouette: tuple[float, ...]   # mean s(i) per cluster


def standardize(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Column-wise z-score; returns (Z, mean, std)."""
    X = np.asarray(X, dtype=float)
    mean, std = X.mean(axis=0), X.std(axis=0, ddof=0)
    std[std == 0] = 1.0
    return (X - mean) / std, mean, std


def fit_kmeans(Z: np.ndarray, k: int) -> np.ndarray:
    """K-Means with locked seed and restarts; returns integer labels."""
    km = KMeans(n_clusters=k, random_state=config.RANDOM_STATE,
                n_init=config.N_INIT)
    return km.fit_predict(Z)


def evaluate(Z: np.ndarray, labels: np.ndarray) -> tuple[float, tuple, tuple]:
    """Global silhouette, cluster sizes, per-cluster mean silhouette."""
    score = float(silhouette_score(Z, labels))
    samples = silhouette_samples(Z, labels)
    sizes, sil = [], []
    for c in np.unique(labels):
        sizes.append(int((labels == c).sum()))
        sil.append(float(samples[labels == c].mean()))
    return score, tuple(sizes), tuple(sil)


def sweep(Z: np.ndarray, k_range: tuple[int, ...] = config.K_RANGE
          ) -> dict[int, SweepResult]:
    """Fit and score every candidate k."""
    out: dict[int, SweepResult] = {}
    for k in k_range:
        labels = fit_kmeans(Z, k)
        score, sizes, sil = evaluate(Z, labels)
        out[k] = SweepResult(k, labels, score, sizes, sil)
    return out


def admissible(results: dict[int, SweepResult]) -> list[int]:
    """Statistical screening C1 (n_c >= N_MIN) and C2 (min S_c >= S_MIN)."""
    ok = []
    for k, r in results.items():
        if min(r.sizes) >= config.N_MIN and min(r.cluster_silhouette) >= config.S_MIN:
            ok.append(k)
    return sorted(ok)


def select_k(results: dict[int, SweepResult], ok: list[int],
             override: int | None = None) -> int:
    """argmax S(k) over admissible k; `override` documents a policy choice."""
    if override is not None:
        return override
    return max(ok, key=lambda k: results[k].score)


def characterize(df: np.ndarray | "pd.DataFrame", labels: np.ndarray,
                 columns: list[str]) -> "pd.DataFrame":
    """Per-cluster centroids (raw units), z-centroids and qualitative labels."""
    import pandas as pd
    Z, mean, std = standardize(np.asarray(df, dtype=float))
    rows = []
    for c in np.unique(labels):
        m = labels == c
        z_cent = Z[m].mean(axis=0)
        lab = ["High" if v >= config.LABEL_THRESHOLD else
               ("Low" if v <= -config.LABEL_THRESHOLD else "Moderate")
               for v in z_cent]
        rows.append({"cluster": int(c), "n": int(m.sum()),
                     **{f"mean_{col}": float(np.asarray(df)[m, j].mean())
                        for j, col in enumerate(columns)},
                     **{f"z_{col}": float(z_cent[j]) for j, col in enumerate(columns)},
                     **{f"label_{col}": lab[j] for j, col in enumerate(columns)}})
    return pd.DataFrame(rows)


def convex_hull(points: np.ndarray, expand: float = 1.10,
                margin: float = 0.035) -> np.ndarray:
    """Closed 2-D boundary polygon around `points` (axis-normalised margin).

    n >= 3 : expanded convex hull;  n == 2 : capsule;  n == 1 : circle.
    """
    pts = np.asarray(points, dtype=float)
    lo, span = pts.min(axis=0), np.ptp(pts, axis=0)
    span[span == 0] = 1.0
    q = (pts - lo) / span
    t = np.linspace(0, 2 * np.pi, 60)

    if len(q) == 1:
        out = np.column_stack([q[0, 0] + margin * np.cos(t),
                               q[0, 1] + margin * np.sin(t)])
    elif len(q) == 2:
        m, d = q.mean(axis=0), q[1] - q[0]
        L = float(np.linalg.norm(d))
        u = d / L if L > 0 else np.array([1.0, 0.0])
        w = np.array([-u[1], u[0]])
        out = (m[:, None] + u[:, None] * ((L / 2 + margin) * np.cos(t))
               + w[:, None] * (margin * 1.15 * np.sin(t))).T
    else:
        from scipy.spatial import ConvexHull
        hp = q[ConvexHull(q).vertices]
        cen = q.mean(axis=0)
        v = hp - cen
        nrm = np.linalg.norm(v, axis=1, keepdims=True)
        nrm[nrm == 0] = 1e-9
        out = cen + v * expand + (v / nrm) * margin
        out = np.vstack([out, out[0]])
    return lo + out * span