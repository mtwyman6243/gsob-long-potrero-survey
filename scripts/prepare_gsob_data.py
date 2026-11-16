"""
prepare_gsob_data.py
---------------------
Parses the Long Potrero GSOB tree-tag survey (BCLT, 2019-2020) into a clean
GeoJSON FeatureCollection for mapping.

This version uses only the standard library + openpyxl so it can run
anywhere without a full geospatial stack installed. If you have GeoPandas
available, `build_gsob_map.py` shows the equivalent GeoDataFrame-based
pattern to reuse for future projects (wildfire hazard, retention basins).

Usage:
    python prepare_gsob_data.py \
        --input "Copy_of_Potrero_Tree__tag_2_0.xlsx" \
        --output "../data/gsob_potrero.geojson"
"""

import argparse
import json
import re

import openpyxl

COORD_RE = re.compile(r"([NSEW])\s*(\d+)\s+(\d+(?:\.\d+)?)'?")


def parse_dm(value):
    """Parse a 'N 32 38.063' style degree/decimal-minute string to decimal degrees."""
    if value is None:
        return None
    m = COORD_RE.match(str(value).strip())
    if not m:
        return None
    hemi, deg, minutes = m.groups()
    dd = float(deg) + float(minutes) / 60.0
    if hemi in ("S", "W"):
        dd *= -1
    return dd


def classify_treatment(crown, holes, stain):
    """Mirrors the treatment logic described in the 2020 GSOB report."""
    if holes is None:
        return "Unclassified"
    if holes >= 4:
        return "Chop & Solarize"
    if holes == 3 and (crown or 0) >= 4:
        return "Chop & Solarize"
    if holes == 3:
        return "Spray / Inject"
    if holes == 2:
        return "Spray / Inject"
    return "Monitor / Healthy"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="../raw/Copy_of_Potrero_Tree__tag_2_0.xlsx")
    ap.add_argument("--output", default="../data/gsob_potrero.geojson")
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.input, data_only=True)
    ws = wb.worksheets[0]

    # This workbook has two stacked tables (a main table, then a second table
    # of previously-unlocated trees that have since had some coordinates
    # added), separated by a header row and a couple of summary rows. Rather
    # than rely on fixed row ranges, scan every row and keep any row that
    # looks like real tree data: integer tag number + a lat string starting
    # with N/S. This skips header rows, blank rows, and "Total 1's:" style
    # summary rows automatically, and works across both tables.
    all_rows = list(ws.iter_rows(min_row=1, values_only=True))

    features = []
    seen_tags = {}
    skipped = 0

    for row in all_rows:
        tag, lat_raw, lon_raw, crown, holes, stain = (row + (None,) * 6)[:6]

        if not isinstance(tag, (int, float)):
            continue
        if not (isinstance(lat_raw, str) and lat_raw.strip().upper().startswith(("N", "S"))):
            skipped += 1 if isinstance(tag, (int, float)) else 0
            continue
        if not (isinstance(lon_raw, str) and lon_raw.strip().upper().startswith(("E", "W"))):
            skipped += 1
            continue

        lat = parse_dm(lat_raw)
        lon = parse_dm(lon_raw)
        if lat is None or lon is None:
            skipped += 1
            continue

        tag = int(tag)
        crown = int(crown) if isinstance(crown, (int, float)) else None
        holes = int(holes) if isinstance(holes, (int, float)) else None
        stain = int(stain) if isinstance(stain, (int, float)) else None
        treatment = classify_treatment(crown, holes, stain)

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {
                "tag": tag,
                "crown_rating": crown,
                "exit_hole_rating": holes,
                "bark_stain_rating": stain,
                "treatment": treatment,
            },
        }

        # If a tag appears in both tables, keep whichever has more complete
        # condition ratings (some second-table entries only have coordinates).
        if tag in seen_tags:
            existing = seen_tags[tag]
            if existing["properties"]["exit_hole_rating"] is not None:
                continue  # existing entry already has ratings; skip this dup
        seen_tags[tag] = feature

    features = list(seen_tags.values())
    fc = {"type": "FeatureCollection", "features": features}

    with open(args.output, "w") as f:
        json.dump(fc, f)

    counts = {}
    for feat in features:
        t = feat["properties"]["treatment"]
        counts[t] = counts.get(t, 0) + 1

    print(f"Parsed {len(features)} trees ({skipped} skipped for missing/malformed coordinates).")
    print("Treatment breakdown:", counts)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
