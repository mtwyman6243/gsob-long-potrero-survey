"""
build_gsob_map.py
------------------
Builds the interactive GSOB Long Potrero web map using leafmap + GeoPandas.

Run this in an environment with the geospatial stack installed:
    pip install leafmap geopandas

This is the canonical version of the pipeline (GeoDataFrame-based). It reads
the GeoJSON produced by prepare_gsob_data.py, adds it to a leafmap.Map with
severity-based styling, and exports a standalone HTML file that gets embedded
in the portfolio site via <iframe>.

Usage:
    python build_gsob_map.py \
        --input ../data/gsob_potrero.geojson \
        --output ../maps/gsob_potrero_map.html
"""

import argparse

import geopandas as gpd
import leafmap.foliumap as leafmap  # folium backend -> exports cleanly to static HTML

TREATMENT_COLORS = {
    "Chop & Solarize": "#a8451f",   # rust — highest priority
    "Spray / Inject": "#b9862f",    # gold — moderate priority
    "Monitor / Healthy": "#2b5b57",  # teal — low priority / healthy
    "Unclassified": "#8a8a8a",
}


def style_fn(feature):
    treatment = feature["properties"].get("treatment", "Unclassified")
    color = TREATMENT_COLORS.get(treatment, "#8a8a8a")
    return {
        "radius": 4,
        "color": color,
        "fillColor": color,
        "fillOpacity": 0.85,
        "weight": 1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="../data/gsob_potrero.geojson")
    ap.add_argument("--output", default="../maps/gsob_potrero_map.html")
    args = ap.parse_args()

    gdf = gpd.read_file(args.input)
    center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]

    m = leafmap.Map(center=center, zoom=15, tiles="Esri.WorldImagery")
    m.add_basemap("OpenStreetMap")

    m.add_gdf(
        gdf,
        layer_name="GSOB Survey — Long Potrero (2020)",
        style_function=style_fn,
        marker_type="circle_marker",
        info_mode="on_hover",
        fields=["tag", "crown_rating", "exit_hole_rating", "bark_stain_rating", "treatment"],
    )

    m.add_legend(
        title="Treatment Recommendation",
        legend_dict=TREATMENT_COLORS,
    )

    m.to_html(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
