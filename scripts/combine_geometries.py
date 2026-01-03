import json
from pathlib import Path


GADM_DIR = Path("data/geometries/gadm")


def merge_geojson_features(input_path: Path, output_path: Path):
    """
    Merge all GeoJSON files in input_dir into a single FeatureCollection
    and write it to output_filepath.

    Args:
        input_dir (Path): Directory to search for GeoJSON files
        output_filepath (Path): File path to save the merged GeoJSON
    """
    all_features = []

    for geojson_file in input_path.rglob("*.geojson"):
        with open(geojson_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data["type"] == "Feature":
                all_features.append(data)
            elif data["type"] == "FeatureCollection":
                all_features.extend(data["features"])

    combined = {
        "type": "FeatureCollection",
        "features": all_features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f)

    print(f"> Merged {len(all_features)} features into {output_path}")


if __name__ == "__main__":
    merge_geojson_features(GADM_DIR, GADM_DIR.parent /
                           "gadm_all_countries.geojson")
