import rasterio
import numpy as np
from pathlib import Path

folder = Path(__file__).parent

# Search inside the project folder and its subfolders
files = list(folder.rglob("*.tif")) + list(folder.rglob("*.tiff"))

b04_files = [f for f in files if "B04" in f.name.upper()]
b08_files = [f for f in files if "B08" in f.name.upper()]

if not b04_files or not b08_files:
    print("B04 ya B08 file nahi mili.")
else:
    red_file = b04_files[0]
    nir_file = b08_files[0]

    print("Red:", red_file.name)
    print("NIR:", nir_file.name)

    with rasterio.open(red_file) as red_src, rasterio.open(nir_file) as nir_src:
        if (red_src.shape != nir_src.shape or
            red_src.transform != nir_src.transform or
            red_src.crs != nir_src.crs):
            print("Error: Dono bands ki dimensions ya alignment match nahi karti.")
        else:
            red = red_src.read(1).astype("float32")
            nir = nir_src.read(1).astype("float32")

            valid = np.isfinite(red) & np.isfinite(nir)

            if red_src.nodata is not None:
                valid &= red != red_src.nodata
            if nir_src.nodata is not None:
                valid &= nir != nir_src.nodata

            denominator = red + nir
            valid &= denominator > 0

            ndvi = np.full(red.shape, np.nan, dtype="float32")
            ndvi[valid] = (nir[valid] - red[valid]) / denominator[valid]

            if not np.any(np.isfinite(ndvi)):
                print("Valid pixels nahi mile.")
            else:
                output = folder / "meerut_real_ndvi.tif"
                profile = red_src.profile.copy()
                profile.update(
                    driver="GTiff",
                    count=1,
                    dtype="float32",
                    nodata=-9999
                )

                with rasterio.open(output, "w", **profile) as dst:
                    dst.write(
                        np.where(np.isfinite(ndvi), ndvi, -9999).astype("float32"),
                        1
                    )

                print("NDVI file saved:", output.name)
                print("Minimum:", float(np.nanmin(ndvi)))
                print("Maximum:", float(np.nanmax(ndvi)))
                print("NDVI calculation complete!")