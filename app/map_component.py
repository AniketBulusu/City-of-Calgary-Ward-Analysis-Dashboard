import geopandas as gpd
import pandas as pd
import folium
from shapely import wkt
from dash import html
import os
from sqlalchemy import create_engine

# Reuse the same database configuration as app.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://appuser:app_password@db:5432/calgary_ward_db",
)

# Create a single engine instance to be reused
_engine = None

def get_engine():
    """Get or create the database engine singleton."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
    return _engine

def generate_ward_map():
    engine = get_engine()

    # Load geometry table
    wards = pd.read_sql("""
        SELECT "WARD_NUM", "MULTIPOLYGON", "COUNCILLOR", "LABEL"
        FROM ward_boundaries_20251117;
    """, con=engine)

    if wards.empty:
        print("WARNING: ward_boundaries_20251117 is empty.")
        return

    wards["geometry"] = wards["MULTIPOLYGON"].apply(wkt.loads)
    wards.rename(columns={"WARD_NUM": "ward"}, inplace=True)

    # Population
    population = pd.read_sql("""
        SELECT ward_number, total AS population
        FROM ward_population;
    """, con=engine).rename(columns={"ward_number": "ward"})

    # Crime
    crime = pd.read_sql("""
        SELECT ward_number, total AS total_crime
        FROM ward_crime;
    """, con=engine).rename(columns={"ward_number": "ward"})

    # Disorder
    disorder = pd.read_sql("""
        SELECT ward_number, total AS total_disorder
        FROM ward_disorder;
    """, con=engine).rename(columns={"ward_number": "ward"})

    # Community services
    services = pd.read_sql("""
        SELECT ward_number, SUM(count) AS services
        FROM community_services
        GROUP BY ward_number;
    """, con=engine).rename(columns={"ward_number": "ward"})

    # Turnout
    turnout = pd.read_sql("""
        SELECT
            vs.ward_number AS ward,
            COALESCE(SUM(er.votes), 0) AS total_votes
        FROM voting_station vs
        LEFT JOIN election_result er ON vs.station_code = er.station_code
        GROUP BY vs.ward_number;
    """, con=engine)

    # Merge all tables safely
    merged = (
        wards
        .merge(population, on="ward", how="left")
        .merge(turnout, on="ward", how="left")
        .merge(crime, on="ward", how="left")
        .merge(disorder, on="ward", how="left")
        .merge(services, on="ward", how="left")
    )

    # Compute turnout percentage
    merged["turnout_rate"] = (
        (merged["total_votes"] / merged["population"]) * 100
    ).fillna(0).round(1)

    # Build GeoDataFrame
    gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")

    # Generate Folium map
    m = folium.Map(location=[51.05, -114.07], zoom_start=10, tiles="cartodbpositron")

    folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "ward",
                "COUNCILLOR",
                "population",
                "turnout_rate",
                "total_crime",
                "total_disorder",
                "services",
            ],
            aliases=[
                "Ward:",
                "Councillor:",
                "Population:",
                "Turnout Rate (%):",
                "Total Crime:",
                "Total Disorder:",
                "Community Services:",
            ],
            localize=True,
            sticky=True,
        ),
        style_function=lambda x: {
            "color": "black",
            "weight": 1,
            "fillColor": "#66c2a5",
            "fillOpacity": 0.55,
        },
    ).add_to(m)

    m.save("ward_map.html")
    print("Saved ward_map.html")


def ward_map_component():
    try:
        src = open("ward_map.html", "r").read()
    except FileNotFoundError:
        generate_ward_map()
        src = open("ward_map.html", "r").read()

    return html.Iframe(
        id="ward-map",
        srcDoc=src,
        width="100%",
        height="600",
        style={"border": "none", "borderRadius": "8px"},
    )