import openeo
from pathlib import Path

OUTPUT_DIR = Path("./worldcereal_jordan_irrigation")
OUTPUT_DIR.mkdir(exist_ok=True)

# Jordan bounding box split into north/south halves so each stays under the
# backend pixel-count threshold (1e11). Full-country extent is ~1.36e11 px.
TILES = {
    "jordan_south": {"west": 34.88, "south": 29.18, "east": 39.30, "north": 31.28},
    "jordan_north": {"west": 34.88, "south": 31.28, "east": 39.30, "north": 33.38},
}

# Jobs already submitted in prior runs (attach instead of resubmitting).
EXISTING_JOBS: dict[str, str] = {}

# Crop-dense northern half (Jordan Valley, Amman, Irbid) needs more memory —
# 3G caused OOM during export. 5G per forum troubleshooting advice.
JOB_OPTIONS = {"executor-memory": "5G"}

connection = openeo.connect("openeofed.dataspace.copernicus.eu")
connection.authenticate_oidc()

for tile_name, extent in TILES.items():
    print(f"\n=== {tile_name} ===", flush=True)
    tile_dir = OUTPUT_DIR / tile_name
    tile_dir.mkdir(exist_ok=True)

    if any(tile_dir.glob("*.tif")):
        print(f"Skipping {tile_name}: already has .tif files", flush=True)
        continue

    if tile_name in EXISTING_JOBS:
        job = connection.job(EXISTING_JOBS[tile_name])
        print(f"Attached to existing job: {job.job_id}", flush=True)
    else:
        datacube = connection.load_collection(
            "ESA_WORLDCEREAL_IRRIGATION",
            spatial_extent=extent,
            temporal_extent=["2021-01-01", "2021-12-31"],
        )
        job = datacube.create_job(
            out_format="GTiff",
            job_options=JOB_OPTIONS,
        )
        job.start_job()
        print(f"Job started - ID: {job.job_id}", flush=True)

    status = job.status()
    print(f"Status: {status}", flush=True)
    if status not in ("finished",):
        job.start_and_wait()

    job.get_results().download_files(tile_dir)
    print(f"Done: {tile_dir.resolve()}", flush=True)

print(f"\nAll tiles saved under: {OUTPUT_DIR.resolve()}", flush=True)
