"""Choropleth of cluster membership (optional: needs geopandas + internet)."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from . import config

BOUNDARY_URLS = [
    "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IDN_1.json",
    "https://raw.githubusercontent.com/superpikar/indonesia-geojson/main/"
    "indonesia-province.geojson",
]
_CANON = {  # boundary-name (upper, stripped) -> panel name
    "ACEH": "Aceh", "SUMATERAUTARA": "Sumatera Utara", "RIAU": "Riau",
    "KEPULAUANRIAU": "Kepulauan Riau", "BANGKABELITUNG": "Kepulauan Bangka Belitung",
    "KEPULAUANBANGKABELITUNG": "Kepulauan Bangka Belitung",
    "SUMATERABARAT": "Sumatera Barat", "JAMBI": "Jambi",
    "SUMATERASELATAN": "Sumatera Selatan", "BENGKULU": "Bengkulu",
    "LAMPUNG": "Lampung", "KALIMANTANBARAT": "Kalimantan Barat",
    "KALIMANTANSELATAN": "Kalimantan Selatan", "KALIMANTANTENGAH": "Kalimantan Tengah",
    "KALIMANTANTIMUR": "Kalimantan Timur", "KALIMANTANUTARA": "Kalimantan Utara",
    "DKIJAKARTA": "Daerah Khusus Jakarta", "JAKARTARAYA": "Daerah Khusus Jakarta",
    "BANTEN": "Banten", "JAWABARAT": "Jawa Barat", "JAWATENGAH": "Jawa Tengah",
    "DIYOGYAKARTA": "DIY", "DAERAHISTIMEWAYOGYAKARTA": "DIY", "YOGYAKARTA": "DIY",
    "JAWATIMUR": "Jawa Timur", "BALI": "Bali",
    "NUSATENGGARABARAT": "Nusa Tenggara Barat",
    "NUSATENGGARATIMUR": "Nusa Tenggara Timur",
    "SULAWESIUTARA": "Sulawesi Utara", "SULAWESITENGAH": "Sulawesi Tengah",
    "SULAWESISELATAN": "Sulawesi Selatan", "SULAWESITENGGARA": "Sulawesi Tenggara",
    "GORONTALO": "Gorontalo", "SULAWESIBARAT": "Sulawesi Barat",
    "MALUKU": "Maluku", "MALUKUUTARA": "Maluku Utara",
    "PAPUA": "Papua", "PAPUASELATAN": "Papua", "PAPUATENGAH": "Papua",
    "PAPUAPEGUNUNGAN": "Papua", "PAPUABARAT": "Papua Barat",
    "PAPUABARATDAYA": "Papua Barat",
}


def indonesia_map_figure(df: pd.DataFrame, label_col: str,
                         names: dict[int, str],
                         path: str | Path | None = None) -> None:
    try:
        import geopandas as gpd
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("geopandas not installed; skip the map or "
                           "`pip install geopandas`") from exc
    gdf = None
    for url in BOUNDARY_URLS:
        try:
            gdf = gpd.read_file(url)
            break
        except Exception:
            continue
    if gdf is None:
        raise RuntimeError("boundary download failed (offline?)")
    name_col = next(c for c in gdf.columns
                    if c.lower() in ("name_1", "propinsi", "provinsi", "name"))
    gdf["province"] = gdf[name_col].map(
        lambda s: _CANON.get(re.sub(r"[^A-Z]", "", str(s).upper())))
    if gdf.province.nunique() < len(gdf):          # merge new Papua splits
        gdf = gdf.dissolve(by="province").reset_index()
    gdf = gdf.merge(df[["province", label_col]], on="province", how="left")
    gdf["fill"] = gdf[label_col].map(config.CLUSTER_COLORS)

    fig, ax = plt.subplots(figsize=(13, 8))
    gdf.plot(color=gdf.fill, ax=ax, edgecolor="0.25", linewidth=.4)
    ax.set_axis_off()
    ax.set_title("Province clusters, Indonesia", fontweight="bold")
    ax.legend(handles=[Patch(facecolor=config.CLUSTER_COLORS[c], label=names[c])
                       for c in sorted(names)], loc="lower left", fontsize=10)
    fig.tight_layout()
    if path is not None:
        fig.savefig(path, dpi=config.DPI, bbox_inches="tight")
    plt.close(fig)