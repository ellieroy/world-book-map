import json
import requests
import pandas as pd
from pathlib import Path


BOOK_JSON = 'data/reference/book_data_template.json'
OUTPUT_DIR = 'data/geometries/gadm'


def download_gadm_geojson(iso_code: str, output_path: str) -> None:
    """
    Downloads a geojson file from the GADM website and saves it to the specified path.
    Skips downloading if the file already exists.

    Args:
        iso_code (str): iso alpha 3 country code (e.g. 'AFG')
        output_path (str): local path to save geojson
    """
    if Path(output_path).exists():
        print(f"> File already exists, skipping download: {output_path}")
        return

    gadm_url = f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso_code}_0.json'

    try:
        response = requests.get(gadm_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            print(f"> Saved GeoJSON: {output_path}")
        else:
            print(
                f"> Failed to download from {gadm_url} (status {response.status_code})")
    except requests.RequestException as e:
        print(f"> Request error for {gadm_url}: {e}")


if __name__ == "__main__":

    df = pd.read_json(BOOK_JSON, orient='index')

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    for code, country in zip(df.index, df['name']):
        geojson_path = f'{OUTPUT_DIR}/{code}_{country.replace(" ", "_")}.geojson'
        download_gadm_geojson(code, geojson_path)
