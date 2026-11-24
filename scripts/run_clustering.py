"""Run the silhouette sweep, select k, and export memberships + centroids.

Example:
    python scripts/run_clustering.py --layer trajectory --force-k 2 --outdir outputs
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from epcluster import clustering, config, data


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data/province_panel.csv")
    ap.add_argument("--layer", choices=sorted(config.LAYERS), default="trajectory")
    ap.add_argument("--force-k", type=int, default=None,
                    help="override the statistical selection (policy decision)")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    df = data.load_panel(args.data)
    cols = list(config.LAYERS[args.layer])
    Z, _, _ = clustering.standardize(data.layer_matrix(df, args.layer).to_numpy())

    results = clustering.sweep(Z)
    ok = clustering.admissible(results)
    k = clustering.select_k(results, ok, override=args.force_k)

    print(f"layer={args.layer}  admissible k (C1,C2)={ok}")
    for kk in sorted(results):
        r = results[kk]
        flag = " <- adopted" if kk == k else ""
        print(f"  k={kk}: S={r.score:.4f} sizes={r.sizes}{flag}")

    labels = results[k].labels if not args.force_k else clustering.fit_kmeans(Z, k)
    df["cluster"] = labels
    df[["province", "cluster"] + cols].to_csv(out / f"membership_{args.layer}.csv",
                                              index=False)
    clustering.characterize(data.layer_matrix(df, args.layer).to_numpy(),
                            labels, cols).to_csv(out / f"centroids_{args.layer}.csv",
                                                 index=False)
    (out / f"summary_{args.layer}.json").write_text(json.dumps(
        {"layer": args.layer, "k": k, "admissible": ok,
         "silhouette": {str(kk): round(results[kk].score, 4) for kk in results},
         "seed": config.RANDOM_STATE, "n_init": config.N_INIT}, indent=2))
    print(f"written: membership, centroids, summary -> {out}/")


if __name__ == "__main__":
    main()