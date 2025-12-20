#!/bin/bash

set -e  # exit on error

# Move to directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
DATA_DIR="$PROJECT_ROOT/data/raw"
mkdir -p "$DATA_DIR"

OUTPUT_FILE="$DATA_DIR/imf_renewable_energy.csv"
echo "Downloading energy data..."
curl -L \
  "https://hub.arcgis.com/api/v3/datasets/0bfab7fb7e0e4050b82bba40cd7a1bd5_0/downloads/data?format=csv&spatialRefId=4326&where=1%3D1" \
  -o "$OUTPUT_FILE"
echo "Data downloaded to $OUTPUT_FILE"

# source https://www.naturalearthdata.com/downloads/110m-cultural-vectors/ 
echo "Downloading natural earth dataset..."
mkdir -p "$DATA_DIR/natural_earth"
OUTPUT_FILE="$DATA_DIR/natural_earth/world_countries.zip"
curl -L \
  "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip" \
  -o "$OUTPUT_FILE"
echo "Data downloaded to $OUTPUT_FILE, unzipping..."
unzip -o "$DATA_DIR"/natural_earth/world_countries.zip -d "$DATA_DIR/natural_earth"
echo "Natural Earth data process complete."

# Fetch ISO codes using Python script
echo "Fetching ISO country codes..."
python3 "$SCRIPT_DIR/fetch_iso_codes.py"
echo "ISO codes fetched successfully."