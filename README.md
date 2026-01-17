# World book map

## Data processing

1. Generate csv of countries with ISO codes and region names (`scripts/get_country_data.py`)
2. Create template book json (`scripts/book_data_template.py`)
3. Manually add book details per country
4. Download gadm boundaries (`scripts/get_geometries.py`)
5. Merge geojsons and simplify - npm scripts