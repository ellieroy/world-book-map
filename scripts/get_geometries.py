import json
from pathlib import Path
import requests
import geopandas as gpd


OUTPUT_DIR = Path("data/geometries/gadm")


def download_gadm_geojson(iso_code: str, output_path: Path) -> None:
    """
    Downloads a GeoJSON file from the GADM website and saves it to the specified path.
    Skips downloading if the file already exists.

    Args:
        iso_code (str): The 3-letter ISO country code (e.g. 'AFG')
        output_path (Path): The local path where the file should be saved
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"> File already exists, skipping download: {output_path}")
        return

    gadm_url = f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso_code}_0.json'

    try:
        response = requests.get(gadm_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            # print(f"> Saved GeoJSON: {output_path}")
        else:
            print(
                f"> Failed to download from {gadm_url} (status {response.status_code})")
    except requests.RequestException as e:
        print(f"> Request error for {gadm_url}: {e}")


if __name__ == "__main__":

    # data_dir = Path("data/books")
    country_codes_path = Path("data/country_data_base.json")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(country_codes_path, "r", encoding="utf-8") as f:
        country_codes_dict = json.load(f)

    countries = country_codes_dict.keys()
    codes = [data["code"] for data in country_codes_dict.values()]

    for code, country in zip(codes, countries):
        download_gadm_geojson(
            code, OUTPUT_DIR / f'{code}_{country.replace(" ", "_")}.geojson')
