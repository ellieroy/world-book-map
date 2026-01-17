"""
Generates a json template file for collecting book data by country.
This json file is organized by each country's iso code and
includes country metadata (country name, continent, region)
along with placeholder content for book information.
"""
import json
import pandas as pd
from pathlib import Path


COUNTRY_INFO_PATH = 'data/reference/country_data.csv'
OUTPUT_JSON_PATH = 'data/reference/book_data_template.json'
ISO_CODES_TO_SKIP = ['XCA', 'XCL', 'XSP',
                     'XPI', 'XAD', 'ATA', 'BVT', 'HMD', 'UMI']


def create_country_record(row: pd.Series) -> dict:
    """Converts a DataFrame row of country data into a structured dictionary entry.
    containing information on the country's name, continent, region and
    a template structure for book data. The region is determined hierarchically,
    using the most-detailed UN geoscheme region available.
    """

    region = ''
    if row['intermediate_region_name'].strip():
        region = row['intermediate_region_name'].strip()
    elif row['sub_region_name'].strip():
        region = row['sub_region_name'].strip()

    return {
        "name": row['name'].strip(),
        "continent": row['region_name'].strip(),
        "region": region,
        "notes": "",
        "books": [
            {
                "title": "",
                "isbn": "",
                "read": 0,
                "notes": ""
            }
        ]
    }


if __name__ == '__main__':

    # Read country info csv
    df = pd.read_csv(COUNTRY_INFO_PATH)

    # Clean-up dataframe
    df = df[~df['iso_alpha3_code'].isin(ISO_CODES_TO_SKIP)]
    df = df.set_index('iso_alpha3_code')
    df = df.fillna('')

    # Generate template content for each country
    country_book_data = df.apply(create_country_record, axis=1).to_dict()

    # Write to json file
    Path(OUTPUT_JSON_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(country_book_data, f, indent=2, ensure_ascii=False)
