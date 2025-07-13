import json
from pathlib import Path
import requests
import geopandas as gpd


def download_gadm_geojson(code_and_level: str, output_path: Path) -> None:
    """
    Downloads a GeoJSON file from the GADM website and saves it to the specified path.
    Skips downloading if the file already exists.

    Args:
        code_and_level (str): The 3-letter ISO country code and GADM level (e.g. 'AFG_0')
        output_path (Path): The local path where the file should be saved
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"> File already exists, skipping download: {output_path}")
        return

    gadm_url = f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{code_and_level}.json'

    try:
        response = requests.get(gadm_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            print(f"> Saved GeoJSON: {output_path}")
        else:
            print(f"> Failed to download from {gadm_url} (status {response.status_code})")
    except requests.RequestException as e:
        print(f"> Request error for {gadm_url}: {e}")


if __name__ == "__main__":

    data_dir = Path("data/books")
    country_codes_path = Path("data/country_codes.json")

    output_dir = Path("data/geometries/gadm")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(country_codes_path, "r", encoding="utf-8") as f:
        country_codes_dict = json.load(f)

    for json_file in data_dir.glob("*.json"):

        with open(json_file, "r", encoding="utf-8") as f:
            region_name = json_file.stem
            region_data = json.load(f)

            if region_name == 'uk-ireland':
                country_codes = [country_codes_dict[country] for country in ['United Kingdom', 'Ireland']]
                levels = [1, 0]
                for code, level in zip(country_codes, levels):
                    download_gadm_geojson(f'{code}_{level}', output_dir / f'europe/{code}.geojson')

            elif region_name == 'america-north':
                country_codes = [country_codes_dict[country] for country in ['United States', 'Canada']]
                levels = [1, 0]
                for code, level in zip(country_codes, levels):
                    download_gadm_geojson(f'{code}_{level}', output_dir / f'america/{code}.geojson')
                    if code == 'USA':
                        with open('data/us_regions.json', "r", encoding="utf-8") as f:
                            us_regions_dict = json.load(f)
                        usa_filepath = output_dir / 'america/USA.geojson'
                        states = gpd.read_file(usa_filepath)
                        states["region"] = states["NAME_1"].map(us_regions_dict)
                        states.to_file(usa_filepath, driver="GeoJSON")

            else:
                country_codes = [country_codes_dict[country] for country in region_data.keys()]
                for code in country_codes:
                    main_region = region_name.split('-')[0]
                    download_gadm_geojson(f'{code}_0', output_dir / f'{main_region}/{code}.geojson')
