# WorldCereal 2021 Irrigation Product — Jordan

Downloaded the ESA WorldCereal 2021 irrigation binary classification over Jordan
via the CDSE openEO backend, working around two backend constraints that the
Processing Hub web UI hits.

## Result

| Tile | File | Size | Extent (WGS84) |
|------|------|------|----------------|
| jordan_south | `worldcereal_jordan_irrigation/jordan_south/openEO_2021-01-01Z.tif` | 23 MB | 34.88, 29.18 → 39.30, 31.28 |
| jordan_north | `worldcereal_jordan_irrigation/jordan_north/openEO_2021-01-01Z.tif` | 106 MB | 34.88, 31.28 → 39.30, 33.38 |

The rasters themselves are **not committed** to this repository (the north tile
exceeds GitHub's 100 MB file limit). Run the script below to regenerate them —
it takes ~15 minutes against the openEO backend.

Jordan ADM1 administrative boundaries from
[geoBoundaries](https://www.geoboundaries.org/) are included under
[`data/geoBoundaries-JOR-ADM1-all/`](data/geoBoundaries-JOR-ADM1-all/) for
clipping/visualization (CC BY 4.0).

## Reproduction

```bash
python3 -m venv ~/worldcereal
source ~/worldcereal/bin/activate
pip install openeo            # installed 0.49.0

python -u download_jordan_irrigation.py
```

On the first run the script pauses once and prints a CDSE login URL. Open it
in a browser, log in, click approve — the script then continues automatically
and caches a refresh token, so later runs don't prompt again.

The script is idempotent: tiles whose output directory already contains a
`.tif` are skipped, so re-runs after a partial failure only retry the missing
tiles.

## Issues encountered (and fixes applied in the script)

1. **Wrong backend.** `ESA_WORLDCEREAL_IRRIGATION` is **not** on
   `openeo.dataspace.copernicus.eu`. It lives on the federated endpoint
   `openeofed.dataspace.copernicus.eu` (terrascope federation). Using the main
   endpoint returns `404 CollectionNotFound`.

2. **Extent too large.** The full Jordan bbox (34.88, 29.18, 39.30, 33.38) at
   10 m resolution is ~1.36e+11 pixels, above the backend's 1.00e+11 threshold.
   Fix: split into north/south halves at latitude 31.28.

3. **OOM on the north tile.** With the default `executor-memory: 3G` (forum
   workaround for the Processing Hub bug), the crop-dense north half (Jordan
   Valley, Amman, Irbid) failed with `Container exit code 52 /
   OutOfMemoryError` after ~70% progress. Fix: bump to `5G`. South half
   completes fine at either setting.



