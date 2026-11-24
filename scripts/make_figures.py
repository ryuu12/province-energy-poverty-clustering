"""Generate all repository figures from a clustering run.

Example:
    python scripts/make_figures.py --layer trajectory --k 2 --map
"""
from __future__ import annotations

import argparse
from pathlib import Path

from epcluster import clustering, config, data, plotting


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data/province_panel.csv")
    ap.add_argument("--layer", choices=sorted(config.LAYERS), default="trajectory")
    ap.add_argument("--k", type=int, default=None,
                    help="default: config.K_TRAJECTORY / K_STATIC_2025")
    ap.add_argument("--outdir", default="outputs")
    ap.add_argument("--map", action="store_true", help="also draw the choropleth")
    args = ap.parse_args()

    out = Path(args.outdir) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    df = data.load_panel(args.data)
    cols = list(config.LAYERS[args.layer])
    Z, _, _ = clustering.standardize(data.layer_matrix(df, args.layer).to_numpy())

    k = args.k or (config.K_TRAJECTORY if args.layer == "trajectory"
                   else config.K_STATIC_2025)
    results = clustering.sweep(Z)
    names = {c: f"Cluster {c}" for c in range(k)}

    plotting.silhouette_sweep_figure(results, k, out / "silhouette_sweep.png")
    if args.layer == "trajectory":
        plotting.hull_scatter_figure(
            df, "d_ur", "d_ep", "d_cdd", "cluster", names,
            annotate=["Bali", "Sumatera Selatan", "DIY", "Jawa Barat",
                      "Daerah Khusus Jakarta", "Jawa Timur"],
            title="Trajectory clusters (k=%d): dUR vs dEP, bubble = dCDD" % k,
            path=out / "hull_scatter_trajectory.png")
        plotting.trajectory_grid_figure(df, "cluster", ("ur", "cdd"), names,
                                        out / "trajectory_grid.png")
    else:
        x, y, s = cols
        plotting.hull_scatter_figure(df, y, x, s, "cluster", names,
                                     title=f"Static {args.layer} hulls (k={k})",
                                     path=out / f"hull_scatter_{args.layer}.png")
    if args.map:
        from epcluster import mapping
        mapping.indonesia_map_figure(df, "cluster", names,
                                     out / f"map_{args.layer}_k{k}.png")
    print(f"figures written to {out}/")


if __name__ == "__main__":
    main()