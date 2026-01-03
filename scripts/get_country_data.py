"""
Generates a JSON file of countries with their ISO codes, UN geoscheme regions and
placeholder values for notes and book entries.
The countries and ISO codes are obtained by scraping the GADM website and the
regions are based on a csv downloaded from https://unstats.un.org/unsd/methodology/m49/overview/.
"""
import json
from pathlib import Path
import requests
import pandas as pd
from bs4 import BeautifulSoup


GADM_URL = "https://gadm.org/maps.html"
REGIONS_CSV = './data/un_geoscheme_regions.csv'
OUTPUT_JSON = './data/country_data_base.json'


if __name__ == '__main__':

    # Get GADM page content
    response = requests.get(GADM_URL, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"  # to read accents correctly
    soup = BeautifulSoup(response.text, "html.parser")

    # Find tag containing country links
    target_tag = soup.find_all("p")[2]

    # Read csv containing region data
    region_df = pd.read_csv(REGIONS_CSV, sep=';')

    country_data = {}
    leading_letter = None

    # Process each <font> and <a> tag in the target tag
    for tag in target_tag.find_all(["font", "a"]):
        if tag.name == "font":
            # Each <font> tag contains a leading alphabet letter (e.g., "A") used as a heading.
            # This is stored temporarily to prepend to the next country name starting with this letter.
            leading_letter = tag.get_text(strip=True)

        elif tag.name == "a":
            # This <a> tag contains the actual country name
            country_name = tag.get_text(strip=True)

            # If a leading letter was found in a previous <font> tag, prepend it
            if leading_letter:
                country_name = leading_letter + country_name
                leading_letter = None  # consume it so it’s only used once

            href = tag.get("href", "")
            code = Path(href).stem if href.startswith("maps/") else None

            # Extract most specific UN geoscheme region for this country using its ISO code
            matching_region = region_df.loc[
                region_df['ISO-alpha3 Code'] == code,
                ['Region Name', 'Sub-region Name', 'Intermediate Region Name']
            ]

            region = ''
            if not matching_region.empty:
                # Convert the row to a list and select the most detailed region available
                # (preference order: Intermediate Region > Sub-region > Region)
                region_values = matching_region.iloc[0].tolist()
                region = next(
                    value for value in reversed(region_values)
                    if pd.notna(value)
                )

            # Add data to country data dictionary
            country_data[country_name] = {
                'code': code,
                'region': region,
                'notes': '',
                'books': [{
                    "title": "",
                    "isbn": "",
                    "read": 0,
                    "notes": ""
                },]
            }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(country_data, f, indent=2, ensure_ascii=False)
