from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
import json
from shapely import wkt 
from shapely.geometry import shape
from sqlalchemy import create_engine
import os

# Define base path for project, allows datasets to be reachable
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"

DATABASE_URL = os.getenv(
    "DATABSE_URL",
    "postgresql+psycopg2://appuser:app_password@localhost:5432/calgary_ward_db",
)

engine = create_engine(DATABASE_URL)

# Basic data standardization
# allows consistent behavior when interacting with the data
def load_csv(name: str)-> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / name)
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )
    return df

app = Dash()

app.layout = [
    html.Div(children='Dashboard'),
    dash_table.DataTable(data=df.to_dict())
]

CHARACTERISTIC_OPTIONS = [

]

ELECTION_OPTIONS = [
    {"label" : "Turnout", "value" : "turnout"},
    {"label" : "Winner", "value" : "winner"}
]

if __name__ == '__main__':
    app.run(debug=True)