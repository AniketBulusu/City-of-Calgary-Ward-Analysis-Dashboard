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
    "DATABASE_URL",
    "postgresql+psycopg2://appuser:app_password@localhost:5432/calgary_ward_db",
)
engine = create_engine(DATABASE_URL)

# QUERY function
# call this every time you need to query the database
def query_db(sql_query, params=None):
    try:
        return pd.read_sql_query(text(sql_query), engine, params=params)
    except Exception as e:
        print(f"Query error: {e}")
        print(f"Query was: {sql_query}")
        raise

# TEST 

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("Database connected.")

        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        rables = [row[0] for row in result]
        print (f'Found {len(tables)} tables: {', '.join(tables)}')
except Exception as e:
    print(f"Database error: {e}")

# WARD BOUNDARY DATA - REPLACE WITH SULTAN'S CODE


# Build APP layout
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Calgary Ward Analysis Dashboard", className="text-center mb-4 mt-4"),
            html.P("Built using PostgreSQL, Python, Plotly, Dash, PgAdmin, pandas, SQLAlchemy, Shapely", className="text-center text-muted"),
            html.P("Authors: Sam Safe, Aniket Bulusu, Sultan Alzoghaibi", className='text-center text-muted'),
        ])
    ]),
    
    dbc.Tabs([
        dbc.Tab(label="Ward Map", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Calgary Ward Map", className="mt-3"),
                    dcc.Graph(id='ward-map', style={'height': '600px'}),
                ], width=12),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.Div(id='ward-detail-panel', className="mt-3")
                ])
            ])
        ]),
        
        dbc.Tab(label="View Data", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Dataset Viewer (SQL Queries)", className="mt-4 mb-3"),
                    
                    html.Label("Select Dataset:", className="fw-bold"),
                    dcc.Dropdown(
                        id='dataset-dropdown',
                        options=[
                            {'label': 'Ward Summary', 'value': 'ward_summary'},
                            {'label': 'Voter Turnout (Calculated)', 'value': 'turnout'},
                            {'label': 'Election Winners', 'value': 'winners'},
                            {'label': 'Population', 'value': 'population'},
                            {'label': 'Crime Statistics', 'value': 'crime'},
                        ],
                        value='ward_summary',
                        clearable=False,
                        className="mb-4"
                    ),
                    
                    html.Div(id='sql-query-display', className="mb-3"),
                    html.Div(id='data-table-container')
                ])
            ])
        ]),
    ], className="mt-3"),
    
], fluid=True)

if __name__ == '__main__':
    print("Dashboard started on http://0.0.0.0:8050")
    app.run(host='0.0.0.0', port=8050, debug=True)