import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Earth Explore",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Earth Explore")
st.subheader("Explore vegetation through NDVI data")

# Load CSV
df = pd.read_csv("ndvi_data.csv")
# Add city coordinates for the map
coordinates = {
    "Delhi": (28.6139, 77.2090),
    "Noida": (28.5355, 77.3910),
    "Ghaziabad": (28.6692, 77.4538),
    "Meerut": (28.9845, 77.7064),
    "Agra": (27.1767, 78.0081)
}

df["latitude"] = df["City"].map(
    lambda city: coordinates[city][0]
)

df["longitude"] = df["City"].map(
    lambda city: coordinates[city][1]
)

# City selector
city = st.selectbox(
    "🔎 Search or select a city",
    options=sorted(df["City"].unique())
)

selected_value = df.loc[df["City"] == city, "NDVI"].iloc[0]
# Selected city information card
st.subheader("📍 Selected City Details")

col1, col2 = st.columns(2)

with col1:
    st.metric("🏙️ City Name", city)

with col2:
    st.metric("🌿 NDVI Value", f"{selected_value:.2f}")

st.caption(
    "Note: The current NDVI values are practice data, "
    "not verified satellite measurements."
)
# Interpret the selected NDVI value
if selected_value >= 0.6:
    interpretation = "High vegetation signal"
elif selected_value >= 0.3:
    interpretation = "Moderate vegetation signal"
elif selected_value >= 0.1:
    interpretation = "Low vegetation signal"
else:
    interpretation = "Very low vegetation signal"

st.subheader("🌿 NDVI Interpretation")
st.write(f"**{city}:** {interpretation}")
if selected_value >= 0.6:
    st.success("🟢 High vegetation signal")
elif selected_value >= 0.3:
    st.info("🟡 Moderate vegetation signal")
elif selected_value >= 0.1:
    st.warning("🟠 Low vegetation signal")
else:
    st.error("🔴 Very low vegetation signal")
st.info(
    "These are simplified interpretation categories for practice data. "
    "Actual vegetation assessment depends on imagery, season, clouds, "
    "and local conditions."
)

# Calculate statistics
highest = df.loc[df["NDVI"].idxmax()]
lowest = df.loc[df["NDVI"].idxmin()]
average = df["NDVI"].mean()

# Summary cards
col1, col2, col3 = st.columns(3)

col1.metric("Selected City NDVI", f"{selected_value:.2f}")
col2.metric("Highest NDVI", f"{highest['NDVI']:.2f}", highest["City"])
col3.metric("Average NDVI", f"{average:.2f}")

st.divider()

# Interactive city filter
# Interactive NDVI slider filter
# NDVI Location Map
st.subheader("🗺️ City-wise NDVI Map")
# Make marker sizes visibly different
df["marker_size"] = df["NDVI"].clip(lower=0) * 1000 + 100

st.map(
    df,
    latitude="latitude",
    longitude="longitude",
    size="marker_size"
)

st.subheader("🌿 Filter Cities by NDVI")

min_ndvi = st.slider(
"Minimum NDVI",
    min_value=-1.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)

filtered_df = df[df["NDVI"] >= min_ndvi]
# Download filtered NDVI data
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download NDVI Data",
    data=csv_data,
    file_name="earth_explore_ndvi.csv",
    mime="text/csv"
)
st.write(
    f"Showing {len(filtered_df)} of {len(df)} cities"
)

if filtered_df.empty:
    st.warning("No cities found. Move the slider lower.")
else:
    st.bar_chart(filtered_df, x="City", y="NDVI")


# Data table
with st.expander("View all NDVI data"):
    st.dataframe(df, use_container_width=True)

st.caption(
    "Note: Current CSV contains practice data, not verified satellite measurements."
)   
st.subheader("🗺️ NDVI Map — Circle Size Comparison")

import pydeck as pdk

map_data = df.copy()
map_data["radius"] = map_data["NDVI"].clip(lower=0) * 30000 + 2000

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position="[longitude, latitude]",
    get_radius="radius",
    get_fill_color="[50, 180, 80, 180]",
    pickable=True,
)

view = pdk.ViewState(
    latitude=28.5,
    longitude=77.5,
    zoom=7,
    pitch=0,
)

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{City} | NDVI: {NDVI}"},
    )
)
# NDVI Legend
st.subheader("🌿 NDVI Legend")

st.markdown("""
🟢 **0.60 and above** — High vegetation signal

🟡 **0.30 to 0.59** — Moderate vegetation signal

🟠 **0.10 to 0.29** — Low vegetation signal

🔴 **Below 0.10** — Very low vegetation signal
""")
from pathlib import Path

st.subheader("🛰️ Real Satellite NDVI Map")

map_file = Path(__file__).parent / "meerut_ndvi_map.png"

if map_file.exists():
    st.image(str(map_file), caption="Meerut — Sentinel-2 NDVI")
else:
    st.warning("NDVI map file nahi mili.")
 # Real Satellite NDVI Statistics
import numpy as np
import rasterio

st.subheader("📊 Real Satellite NDVI Statistics")

ndvi_file = Path(__file__).parent / "meerut_real_ndvi.tif"

if ndvi_file.exists():
    with rasterio.open(ndvi_file) as src:
        ndvi_data = src.read(1).astype("float32")
        nodata = src.nodata

    valid = np.isfinite(ndvi_data)

    if nodata is not None:
        valid &= ndvi_data != nodata

    valid &= (ndvi_data >= -1) & (ndvi_data <= 1)
    values = ndvi_data[valid]

    if values.size > 0:
        average_ndvi = float(np.mean(values))
        high_ndvi_pct = float(np.mean(values > 0.5) * 100)

        col1, col2, col3 = st.columns(3)

        col1.metric("Average NDVI", f"{average_ndvi:.3f}")
        col2.metric("High-NDVI Pixels", f"{high_ndvi_pct:.1f}%")
        col3.metric("Valid Pixels", f"{values.size:,}")
    else:
        st.warning("Valid NDVI pixels nahi mile.")
else:
    st.warning("Real NDVI TIFF file nahi mili.")
 # NDVI Distribution Analysis
st.subheader("📈 NDVI Distribution")

if ndvi_file.exists():
    with rasterio.open(ndvi_file) as src:
        ndvi_data = src.read(1).astype("float32")
        nodata = src.nodata

    valid = np.isfinite(ndvi_data)

    if nodata is not None:
        valid &= ndvi_data != nodata

    valid &= (ndvi_data >= -1) & (ndvi_data <= 1)
    values = ndvi_data[valid]

    if values.size > 0:
        categories = {
            "Low (< 0.2)": int(np.sum(values < 0.2)),
            "Moderate (0.2–0.5)": int(
                np.sum((values >= 0.2) & (values <= 0.5))
            ),
            "High (> 0.5)": int(np.sum(values > 0.5)),
        }

        st.bar_chart(categories)

        total_pixels = sum(categories.values())

        st.write("### Category-wise Percentage")

        for category, count in categories.items():
            percentage = count / total_pixels * 100
            st.write(
                f"**{category}:** {percentage:.1f}% ({count:,} pixels)"
            )
        st.write("### 🌿 NDVI Category Pie Chart")

        st.vega_lite_chart(
            {
                "mark": {"type": "arc", "innerRadius": 50},
                "encoding": {
                    "theta": {
                        "field": "Pixels",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "Category",
                        "type": "nominal",
                        "scale": {
                            "range": ["#E5A04B", "#4C9BE8", "#48A878"]
                        }
                    },
                    "tooltip": [
                        {"field": "Category", "type": "nominal"},
                        {"field": "Pixels", "type": "quantitative"}
                    ]
                },
                "data": {
                    "values": [
                        {"Category": category, "Pixels": count}
                        for category, count in categories.items()
                    ]
                }
            },
            use_container_width=True
        )
        st.caption(
            "Pixel counts by NDVI category. "
            "Thresholds are defined for this project."
        )

    else:
        st.warning("Valid NDVI pixels nahi mile.")

else:
    st.warning("NDVI TIFF file nahi mili.")
# Satellite Observation Date
st.subheader("🛰️ Satellite Observation")

from datetime import date

observation_date = st.date_input(
    "Select observation date",
    value=date(2026, 10, 22),
    min_value=date(2020, 1, 1),
    max_value=date(2026, 12, 31),
    help="Choose the satellite observation date."
)
   
# Satellite Image Information
st.subheader("🛰️ Satellite Image Information")

info1, info2, info3 = st.columns(3)

info1.metric("Study Area", "Meerut, UP")
info2.metric("Satellite", "Sentinel-2")
info3.metric("Data Type", "B04 + B08 NDVI")

st.caption(
    "NDVI = (NIR - Red) / (NIR + Red). "
    "Acquisition date should be verified from the original satellite metadata."
)  
  # ---------- NDVI Date Comparison ----------
import rasterio
import numpy as np
import streamlit as st

st.header("📅 NDVI Comparison: Previous vs 20 Oct 2026")

old_file = "meerut_real_ndvi.tif"
new_file = "meerut_ndvi_oct20.tif"

try:
    with rasterio.open(old_file) as old_src:
        old_data = old_src.read(1).astype("float32")
        old_nodata = old_src.nodata

    with rasterio.open(new_file) as new_src:
        new_data = new_src.read(1).astype("float32")
        new_nodata = new_src.nodata

    def valid_mean(data, nodata):
        valid = np.isfinite(data) & (data >= -1) & (data <= 1)
        if nodata is not None:
            valid &= data != nodata
        if valid.any():
            return float(np.mean(data[valid]))
        return None

    old_mean = valid_mean(old_data, old_nodata)
    new_mean = valid_mean(new_data, new_nodata)

    if old_mean is not None and new_mean is not None:
        col1, col2 = st.columns(2)
        col1.metric("Previous NDVI mean", f"{old_mean:.3f}")
        col2.metric("20 Oct 2026 NDVI mean", f"{new_mean:.3f}")
        st.write("Old raster shape:", old_data.shape)
        st.write("New raster shape:", new_data.shape)

        st.write("Old NDVI min/max:", float(np.nanmin(old_data)), float(np.nanmax(old_data)))
        st.write("New NDVI min/max:", float(np.nanmin(new_data)), float(np.nanmax(new_data)))
        st.write("Old and new arrays identical:", np.array_equal(old_data, new_data))
        st.write("Absolute difference:", float(np.mean(np.abs(old_data - new_data)))) 
        st.bar_chart({
            "Mean NDVI": {
                "Previous observation": old_mean,
                "20 Oct 2026": new_mean
            }
        })
        st.caption(
            "Comparison is meaningful only when both images cover "
            "the same area and use compatible processing."
        )
    else:
        st.warning("Valid NDVI pixels nahi mile. Raster data check karo.")

except Exception as e:
    st.error(f"Comparison error: {e}")