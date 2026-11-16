# Goldspotted Oak Borer Survey — Long Potrero Preserve

A full-preserve field survey of coast live oak and Engelmann oak at Long Potrero Preserve, carried out for the **Back Country Land Trust (BCLT)**. It assessed infestation by the goldspotted oak borer (GSOB), a beetle that has killed more than 80,000 oaks across Southern California.

**[View the interactive webmap →](https://mtwyman6243.github.io/research.html)** · Part of [Matt Twyman's GIS portfolio](https://mtwyman6243.github.io)

## About the project

- 899 trees were tagged, geolocated and scored on three indicators: crown dieback, D-shaped exit-hole density and bark staining.
- 349 of the 899 trees (38.8%) showed GSOB symptoms, up from 33.2% in a 2018 baseline survey.
- The technical report recommended a tiered treatment plan to BCLT: chop-and-solarize for the most severely infested trees, and systemic insecticide or barrier spray for moderate cases. It was co-authored with Megan King and Michael Terlep.

## What's in this repo

```
scripts/
  prepare_gsob_data.py  # parses the tree-tag spreadsheet -> GeoJSON (stdlib + openpyxl)
  build_gsob_map.py     # GeoPandas + leafmap webmap build
data/
  gsob_potrero.geojson  # geolocated trees with symptom scores + treatment class
maps/
  gsob_potrero_map.html # standalone Leaflet webmap, colored by treatment recommendation
```

## The pipeline

1. `prepare_gsob_data.py` reads the raw tree-tag spreadsheet. It finds the coordinate and attribute columns by their content patterns rather than relying on fixed headers, parses each tree's location, assigns a treatment class, and writes GeoJSON.
2. `build_gsob_map.py` loads that GeoJSON into GeoPandas and exports a standalone leafmap/Leaflet HTML map with point styling by severity.

## Running it

The raw survey spreadsheet isn't committed. Put it in a `raw/` folder, then:

```bash
pip install -r requirements.txt
cd scripts
python prepare_gsob_data.py --input "../raw/Copy_of_Potrero_Tree__tag_2_0.xlsx" --output ../data/gsob_potrero.geojson
python build_gsob_map.py --input ../data/gsob_potrero.geojson --output ../maps/gsob_potrero_map.html
```

**Tools:** Field data collection · GPS/GNSS · Python · GeoPandas · leafmap / Leaflet
