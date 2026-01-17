"""
Generates a csv file of countries with their ISO codes and UN geoscheme regions.
The data is obtained by scraping the GADM and UN stats websites.
"""
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup


GADM_URL = "https://gadm.org/download_country.html"
UN_URL = "https://unstats.un.org/unsd/methodology/m49/overview"
OUTPUT_CSV_PATH = 'data/reference/country_data.csv'


if __name__ == '__main__':

    # Extract data from UN geoscheme website
    un_data_df = pd.read_html(UN_URL)[0]
    cols = ['ISO-alpha3 Code', 'Region Name',
            'Sub-region Name', 'Intermediate Region Name']
    un_data_df = un_data_df[cols]

    # Clean up column names
    un_data_df.columns = un_data_df.columns.str.lower(
    ).str.replace(' ', '_').str.replace('-', '_')

    # Get GADM page content
    response = requests.get(GADM_URL, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"  # to read accents correctly
    soup = BeautifulSoup(response.text, "html.parser")

    # Find tag containing dropdown with countries to select
    target_tag = soup.find("select", id='countrySelect')

    # Extract each country from dropdown selection
    # and store country name and iso code in dict
    gadm_dict = {}
    if target_tag:
        options = target_tag.find_all("option")

        for option in options:
            iso_code = option.get('value').split('_')[0]
            country_name = option.text.strip()

            if iso_code == '':
                continue

            gadm_dict[iso_code] = country_name

    # Create dataframe from dict
    gadm_data_df = pd.DataFrame(list(gadm_dict.items()), columns=[
                                'iso_alpha3_code', 'name'])

    # Merge dataframes on iso code and write to csv
    output_df = gadm_data_df.merge(
        un_data_df, on='iso_alpha3_code', how='left')

    Path(OUTPUT_CSV_PATH).parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_CSV_PATH, index=False)
