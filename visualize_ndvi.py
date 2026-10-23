import rasterio
import numpy as np
import matplotlib.pyplot as plt

with rasterio.open("meerut_real_ndvi.tif") as src:
    ndvi = src.read(1).astype("float32")
    nodata = src.nodata

if nodata is not None:
    ndvi[ndvi == nodata] = np.nan

plt.figure(figsize=(10, 7))
plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(label="NDVI")
plt.title("Meerut - Satellite NDVI")
plt.axis("off")
plt.tight_layout()
plt.savefig("meerut_ndvi_map.png", dpi=200)
plt.show()

print("NDVI map saved as meerut_ndvi_map.png")