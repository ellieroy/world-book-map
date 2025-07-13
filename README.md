# World book map

## Environment

### NPM

```
npm init -y
npm install --save-dev mapshaper
```

### Python

```
python3 -m venv venv --upgrade-deps
source venv/bin/activate
pip install -r requirements.txt
```

## Geometry preparation

```
python3 scripts/get_geometries.py
npm run merge_us_states
python3 scripts/combine_geometries.py
npm run simplify_geoms
```