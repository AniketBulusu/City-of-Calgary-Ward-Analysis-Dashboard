from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
import json
from shapely import wkt 
from shapely.geometry import shape
from sqlalchemy import create_engine, text
import os

# Define base path for project, allows datasets to be reachable
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"

# Database URL from ENV
DATABASE_URL = os.getenv(
    "DATABSE_URL",
    "postgresql+psycopg2://appuser:app_password@localhost:5432/calgary_ward_db",
)
engine = create_engine(DATABASE_URL)

# QUERY function
# call this every time you need to query the database
def query_db(sql_query, params=None):
    try:
        return pd.read_sql_query(text(sql_query), engine, params=params)
    except Exception as e:
        print("Query error: {e}")
        print("Query was: {sql_query}")
        raise

# Build APP layout
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = dbc.Container ([
    dbc.Row([
        doc.Col([
            html.H1("Calgary Ward Characteristics Dashboard", className='text-center mb-4 mt-4'),
            html.P("Built using PostgreSQL, Python, Plotly, Dash, PgAdmin, pandas, SQLAlchemy, Shapely", className='text-center text-muted'),
        ])
    ]),

    dbc.Tabs([
        dbc.Tab(label='Ward Map', children =[
            dbc.Row([
                
            ])
        ])

        dbc.Tab(label='View Data', children=[
            dbc.Row([
                dbc.Col([
                    html.H4('Dataset Viewer (SQL Queries)', className='mt-4 mb-3'),
                    html.Label('Select Dataset:', className='fw-bold'),
                    dcc.Dropdown(

                    )
                ])
            ])
        ])
    ])
])

if __name__ == '__main__':
    print("Dashboard started on http://0.0.0.0:8050")
    app.run(host='0.0.0.0', port=8050, debug=True)