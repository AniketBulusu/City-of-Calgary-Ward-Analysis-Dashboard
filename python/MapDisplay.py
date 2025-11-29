import geopandas as gpd
import pandas as pd
import folium
from shapely import wkt
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://sultanalzoghaibi:@localhost:5432/cpsc471-final"
)

df = pd.read_sql("""
    SELECT "WARD_NUM", "MULTIPOLYGON" FROM ward_boundaries_20251117;
""", con=engine)

df["geometry"] = df["MULTIPOLYGON"].apply(wkt.loads)

gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

m = folium.Map(location=[51.05, -114.07], zoom_start=10, tiles="cartodbpositron")

folium.GeoJson(
    gdf,
    tooltip=folium.GeoJsonTooltip(
        fields=["WARD_NUM"],
        aliases=["Ward Number:"],
        localize=True,
        sticky=True
    ),
    style_function=lambda x: {
        "color": "black",
        "weight": 1,
        "fillColor": "#66c2a5",
        "fillOpacity": 0.5
    }
).add_to(m)

# Save and open
m.save("ward_map.html")
print("Map saved as ward_map.html")