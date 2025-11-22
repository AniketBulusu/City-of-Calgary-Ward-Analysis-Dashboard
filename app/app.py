# OS stuff
from pathlib import Path
import os

# DATA stuff
import pandas as pd
from sqlalchemy import create_engine, text

# UI stuff
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

# Set base pash for project
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"

# used by the dash app
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://appuser:app_password@localhost:5432/calgary_ward_db",
)
engine = create_engine(DATABASE_URL)

# Query helper

def query_db(sql_query: str, params=None) -> pd.DataFrame:
    try:
        return pd.read_sql_query(text(sql_query), engine, params=params)
    except Exception as e:
        print(f"Query error: {e}")
        print(f"Query was: {sql_query}")
        raise

# Initialize the app

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Calgary Ward Analysis Dashboard"  # browser tab title


def make_metric_card(title: str, value: str, subtitle: str = ""):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title text-muted mb-1"),
            html.H4(value, className="card-text mb-0"),
            html.Small(subtitle, className="text-muted"),
        ]),
        className="mb-3 shadow-sm",
    )

# Define app layout

app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Calgary Ward Analysis Dashboard",
                        className="text-center mt-4 mb-2",
                    ),
                    html.P(
                        "Built with PostgreSQL, Python, Plotly, Dash, SQLAlchemy, and Shapely",
                        className="text-center text-muted mb-1",
                    ),
                    html.P(
                        "Authors: Sam Safe, Aniket Bulusu, Sultan Alzoghaibi",
                        className="text-center text-muted mb-3",
                    ),
                    html.Hr(),
                ],
                width=12,
            )
        ),

        # Main tabs
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Ward Explorer",
                    tab_id="tab-ward-explorer",
                    children=[
                        dbc.Row(
                            [
                                ############################################# MAP GOES HERE
                                dbc.Col(
                                    [
                                        html.H4(
                                            "Calgary Ward Map",
                                            className="mt-3 mb-2",
                                        ),
                                        html.P(
                                            "Click on a ward to see key metrics and summary information.",
                                            className="text-muted",
                                        ),
                                        dcc.Graph(  #### MAP PLACE HOLDER
                                            id="ward-map",
                                            style={"height": "600px"},
                                            config={"displayModeBar": True},
                                            figure=go.Figure(),  
                                        ),
                                    ],
                                    width=8,
                                ),

                                ###################################################### WARD SUMMARY GOES HERE
                                # Ward details panel extends from the map on the left
                                dbc.Col(
                                    [
                                        html.H4(
                                            "Ward Summary",
                                            className="mt-3 mb-2",
                                        ),
                                        html.Div(
                                            id="ward-detail-panel",
                                            children=[
                                                html.P(
                                                    "Select a ward on the map to view details.",
                                                    className="text-muted",
                                                )
                                            ],
                                        ),
                                    ],
                                    width=4,
                                ),
                            ]
                        ),
                        dcc.Store(id="selected-ward-store"),  
                    ],
                ),

                ####################################################### VISUALIZATIONS GO HERE
                dbc.Tab(
                    label="Visualizations",
                    tab_id="tab-visualizations",
                    children=[
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.H4(
                                        "Analysis & Visualizations",
                                        className="mt-3 mb-3",
                                    ),
                                    html.P(
                                        "Explore relationships between ward characteristics and political outcomes. "
                                        "Curated set provides a baked in overview - switch to custom analysis to build your own comparisons.",
                                        className="text-muted",
                                    ),
                                ],
                                width=12,
                            )
                        ),

                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Curated Set",
                                    tab_id="tab-set",
                                    children=[
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Select a category:",
                                                            className="fw-bold mt-3",
                                                        ),
                                                        dcc.Dropdown(
                                                            id="curated-select",
                                                            options=[
                                                                {
                                                                    "label": "Turnout vs Population",
                                                                    "value": "curated_population_turnout",
                                                                },
                                                                {
                                                                    "label": "Economy & Turnout (Labour Force, Income)",
                                                                    "value": "curated_economy_turnout",
                                                                },
                                                                {
                                                                    "label": "Services, Safety & Turnout",
                                                                    "value": "curated_services_safety",
                                                                },
                                                                {
                                                                    "label": "Mayoral Candidates Across Wards",
                                                                    "value": "curated_candidates",
                                                                },
                                                            ],
                                                            value="curated_population_turnout",
                                                            clearable=False,
                                                            className="mb-3",
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            id="curated-description",
                                                            className="mt-3 mb-2 text-muted",
                                                        ),
                                                    ],
                                                    width=8,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dcc.Graph(
                                                            id="curated-viz-graph",
                                                            style={"height": "600px"},
                                                        )
                                                    ],
                                                    width=12,
                                                )
                                            ]
                                        ),
                                    ],
                                ),

                                dbc.Tab(
                                    label="Custom Analysis",
                                    tab_id="tab-custom",
                                    children=[
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H5(
                                                            "Build Your Own Relationship",
                                                            className="mt-3 mb-3",
                                                        ),
                                                        dbc.Card(
                                                            dbc.CardBody(
                                                                [
                                                                    html.Label(
                                                                        "Characteristic (X-axis):",
                                                                        className="fw-bold",
                                                                    ),
                                                                    dcc.Dropdown(
                                                                        id="characteristic-dropdown",
                                                                        options=[
                                                                            {"label": "Population", "value": "population"},
                                                                            {"label": "Crime", "value": "crime"},
                                                                            {"label": "Disorder", "value": "disorder"},
                                                                            {"label": "Labour Force", "value": "labour"},
                                                                            {"label": "Education (Post-Secondary)", "value": "education"},
                                                                            {"label": "Average Income", "value": "income"},
                                                                            {"label": "Community Services", "value": "services"},
                                                                            {"label": "Recreation Facilities", "value": "recreation"},
                                                                            {"label": "Transit Stops", "value": "transit"},
                                                                            {"label": "Public Transit Users", "value": "work_transit"},
                                                                        ],
                                                                        placeholder="Select a ward characteristic…",
                                                                        className="mb-3",
                                                                    ),
                                                                    html.Label(
                                                                        "Politics (Y-axis):",
                                                                        className="fw-bold",
                                                                    ),
                                                                    dcc.Dropdown(
                                                                        id="politics-dropdown",
                                                                        options=[
                                                                            {"label": "Voter Turnout (Total Votes)", "value": "turnout"},
                                                                            {"label": "Winning Candidate / Vote Share", "value": "winner"},
                                                                        ],
                                                                        placeholder="Select a political outcome…",
                                                                        className="mb-3",
                                                                    ),
                                                                    dbc.Button(
                                                                        "Generate Visualization",
                                                                        id="custom-viz-apply",
                                                                        color="primary",
                                                                        className="mt-1",
                                                                    ),
                                                                    html.Div(
                                                                        id="custom-viz-message",
                                                                        className="mt-2 text-muted",
                                                                    ),
                                                                ]
                                                            ),
                                                            className="shadow-sm",
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dcc.Graph(
                                                            id="custom-viz-graph",
                                                            style={"height": "600px"},
                                                        )
                                                    ],
                                                    width=8,
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                            className="mt-2",
                        ),
                    ],
                ),

                dbc.Tab(
                    label="Data View",
                    tab_id="tab-data-view",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4(
                                            "Dataset Viewer (SQL Queries)",
                                            className="mt-4 mb-3",
                                        ),
                                        html.Label(
                                            "Select Dataset:",
                                            className="fw-bold",
                                        ),
                                        dcc.Dropdown(
                                            id="dataset-dropdown",
                                            options=[
                                                {'label': 'Ward List', 'value': 'ward_summary'},
                                                {'label': 'Population', 'value': 'ward_population'},
                                                {'label': 'Crime', 'value': 'ward_crime'},
                                                {'label': 'Disorder', 'value': 'ward_disorder'},
                                                {'label': 'Age & Gender', 'value': 'ward_age_gender'},
                                                {'label': 'Education', 'value': 'ward_education'},
                                                {'label': 'Income', 'value': 'ward_income'},
                                                {'label': 'Labour Force', 'value': 'ward_labour_force'},
                                                {'label': 'Transport Modes', 'value': 'ward_transport_mode'},
                                                {'label': 'Transit Stops', 'value': 'ward_transit_stops'},
                                                {'label': ' Recreation', 'value': 'ward_recreation'},
                                                {'label': 'Community Services', 'value': 'community_services'},
                                                {'label': 'Election Info', 'value': 'election'},
                                                {'label': 'Races', 'value': 'race'},
                                                {'label': 'Candidates', 'value': 'candidate'},
                                                {'label': 'Voting Stations', 'value': 'voting_station'},
                                                {'label': 'Election Results (Raw)', 'value': 'election_result'},
                                                {'label': 'Voter Turnout (Calculated)', 'value': 'turnout'},
                                                {'label': 'Election Winners', 'value': 'winners'},
                                            ],
                                            value='ward_summary',
                                            clearable=False,
                                            className="mb-4"
                                        ),
                                        html.Div(
                                            id="sql-query-display",
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            id="data-table-container"
                                        ),
                                    ],
                                    width=12,
                                )
                            ]
                        ),
                    ],
                ),

                dbc.Tab(
                    label="About",
                    tab_id="tab-about",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4(
                                            "About This Project",
                                            className="mt-4 mb-3",
                                        ),
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "This dashboard explores relationships between ward-level "
                                                        "characteristics in Calgary (population, income, crime, "
                                                        "services, transit, etc.) and political outcomes in the 2021 "
                                                        "municipal election.",
                                                        className="mb-2",
                                                    ),
                                                    html.P(
                                                        "The backend uses a normalized PostgreSQL schema with tables "
                                                        "for wards, demographics, services, and detailed election "
                                                        "results by voting station. Visualizations are generated "
                                                        "on-demand using SQL queries, pandas, Plotly, and Streamlit.",
                                                        className="mb-2",
                                                    ),
                                                    html.P(
                                                        "Use the Ward Explorer to interact with individual wards, "
                                                        "the Visualizations tab for both curated and custom analysis,"
                                                        "and the Data View tab to inspect the underlying datasets.",
                                                        className="mb-0",
                                                    ),
                                                ]
                                            ),
                                            className="shadow-sm",
                                        ),
                                    ],
                                    width=8,
                                ),
                            ],
                            justify="center",
                        )
                    ],
                ),
            ],
            id="main-tabs",
            active_tab="tab-ward-explorer",
            className="mt-2",
        ),
    ],
    fluid=True,
)

####################### CALL BACKS

# ---- Ward Explorer: map + details ----

@app.callback(
    Output("selected-ward-store", "data"),
    Input("ward-map", "clickData"),
    prevent_initial_call=True,
)
def store_selected_ward(click_data):
    if not click_data:
        return None
    point = click_data["points"][0]
    ward_number = point.get("customdata")
    return {"ward_number": ward_number}


@app.callback(
    Output("ward-detail-panel", "children"),
    Output("ward-breakdown-charts", "children"),
    Input("selected-ward-store", "data"),
)
def update_ward_details(selected_ward):
    if not selected_ward or selected_ward.get("ward_number") is None:
        return (
            html.P("Select a ward on the map to view details.", className="text-muted"),
            html.P("Ward-specific breakdowns will appear here.", className="text-muted"),
        )

    ward_number = selected_ward["ward_number"]
    population = "N/A"
    turnout_rate = "N/A"
    crime_rate = "N/A"
    avg_income = "N/A"
    winner = "N/A"

    detail_children = [
        html.H5(f"Ward {ward_number}", className="mb-3"),
        make_metric_card("Population", str(population)),
        make_metric_card("Turnout Rate", str(turnout_rate)),
        make_metric_card("Crime Rate (per 1,000)", str(crime_rate)),
        make_metric_card("Average Household Income", str(avg_income)),
        make_metric_card("Winning Mayoral Candidate", str(winner)),
    ]

    breakdown_children = [
        html.P(f"Mini-charts for Ward {ward_number} will go here.", className="text-muted")
    ]

    return detail_children, breakdown_children


# ---- Curated Sets ----

@app.callback(
    Output("curated-viz-graph", "figure"),
    Output("curated-description", "children"),
    Input("curated-select", "value"),
)
def update_curated_visualization(curated_id):
    fig = go.Figure()

    if curated_id == "curated_population_turnout":
        fig.update_layout(title="Turnout vs Population (placeholder)", xaxis_title="Ward", yaxis_title="Value")
        desc = "This visualization will compare ward population to total voter turnout."

    elif curated_id == "curated_economy_turnout":
        fig.update_layout(title="Economy & Turnout (placeholder)", xaxis_title="Economic Measures", yaxis_title="Turnout")
        desc = "This visualization will connect labour force participation and household income to voter turnout."

    elif curated_id == "curated_services_safety":
        fig.update_layout(title="Services, Safety & Turnout (placeholder)", xaxis_title="Service / Safety Index", yaxis_title="Turnout")
        desc = "This visualization will examine whether access to community services and crime levels are associated with turnout."

    elif curated_id == "curated_candidates":
        fig.update_layout(title="Mayoral Candidates Across Wards (placeholder)", xaxis_title="Ward", yaxis_title="Votes")
        desc = "This visualization will highlight where different mayoral candidates performed best."

    else:
        fig.update_layout(title="Select a curated set")
        desc = "Select a curated set from the dropdown."

    return fig, desc


# ---- Custom Analysis ----

@app.callback(
    Output("custom-viz-graph", "figure"),
    Output("custom-viz-message", "children"),
    Input("custom-viz-apply", "n_clicks"),
    State("characteristic-dropdown", "value"),
    State("politics-dropdown", "value"),
    prevent_initial_call=True,
)
def update_custom_visualization(n_clicks, characteristic, politics):
    fig = go.Figure()

    if not characteristic or not politics:
        fig.update_layout(title="Select options to generate a visualization")
        return fig, "Please select both a characteristic and a political outcome."

    fig.update_layout(
        title=f"Custom Visualization: {characteristic} vs {politics} (placeholder)",
        xaxis_title=f"{characteristic}",
        yaxis_title=f"{politics}",
    )

    msg = f"Showing placeholder visualization for '{characteristic}' against '{politics}'."
    return fig, msg

### DATA VIEW

@app.callback(
    Output("sql-query-display", "children"),
    Output("data-table-container", "children"),
    Input("dataset-dropdown", "value"),
)
def update_dataset_view(selected_dataset):
    table_queries = {
        'ward_summary': {
            'sql': 'SELECT * FROM ward ORDER BY ward_number',
            'description': 'All Calgary wards (1-14)'
        },
        'ward_population': {
            'sql': 'SELECT * FROM ward_population ORDER BY ward_number',
            'description': 'Population statistics by ward'
        },
        'ward_crime': {
            'sql': 'SELECT * FROM ward_crime ORDER BY ward_number',
            'description': 'Crime statistics by ward'
        },
        'ward_disorder': {
            'sql': 'SELECT * FROM ward_disorder ORDER BY ward_number',
            'description': 'Disorder incidents by ward'
        },
        'ward_age_gender': {
            'sql': 'SELECT * FROM ward_age_gender ORDER BY ward_number, age_group LIMIT 100',
            'description': 'Population by age and gender (first 100 rows)'
        },
        'ward_education': {
            'sql': 'SELECT * FROM ward_education ORDER BY ward_number, education_level LIMIT 100',
            'description': 'Education levels by ward (first 100 rows)'
        },
        'ward_income': {
            'sql': 'SELECT * FROM ward_income ORDER BY ward_number, income_group LIMIT 100',
            'description': 'Household income distribution (first 100 rows)'
        },
        'ward_labour_force': {
            'sql': 'SELECT * FROM ward_labour_force ORDER BY ward_number, gender',
            'description': 'Labour force statistics'
        },
        'ward_transport_mode': {
            'sql': 'SELECT * FROM ward_transport_mode ORDER BY ward_number, transport_mode LIMIT 100',
            'description': 'Transportation modes (first 100 rows)'
        },
        'ward_transit_stops': {
            'sql': 'SELECT * FROM ward_transit_stops ORDER BY ward_number',
            'description': 'Transit stops by ward'
        },
        'ward_recreation': {
            'sql': 'SELECT * FROM ward_recreation ORDER BY ward_number, facility_type LIMIT 100',
            'description': 'Recreation facilities (first 100 rows)'
        },
        'community_services': {
            'sql': 'SELECT * FROM community_services ORDER BY ward_number, service_type LIMIT 100',
            'description': 'Community services (first 100 rows)'
        },
        'election': {
            'sql': 'SELECT * FROM election',
            'description': '2021 Municipal Election'
        },
        'race': {
            'sql': 'SELECT * FROM race ORDER BY race_id',
            'description': 'Election races (Mayor + 14 Councillors)'
        },
        'candidate': {
            'sql': 'SELECT * FROM candidate ORDER BY name LIMIT 100',
            'description': 'Candidates (first 100)'
        },
        'voting_station': {
            'sql': 'SELECT * FROM voting_station ORDER BY ward_number, station_code LIMIT 100',
            'description': 'Voting stations (first 100)'
        },
        'election_result': {
            'sql': '''
                SELECT 
                    er.station_code,
                    c.name as candidate_name,
                    r.type as race_type,
                    vs.ward_number,
                    er.votes
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                ORDER BY vs.ward_number, er.station_code, er.votes DESC
                LIMIT 200
            ''',
            'description': 'Election results with candidate names (200 of ~47,000 rows)'
        },
        'turnout': {
            'sql': '''
                SELECT
                    vs.ward_number,
                    COUNT(DISTINCT er.station_code) as num_stations,
                    SUM(er.votes) AS total_votes,
                    wp.total AS population,
                    ROUND(
                        CASE 
                            WHEN wp.total > 0 THEN 100.0 * SUM(er.votes)::numeric / wp.total
                            ELSE NULL
                        END, 2
                    ) AS turnout_rate_percent
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                LEFT JOIN ward_population wp ON vs.ward_number = wp.ward_number
                GROUP BY vs.ward_number, wp.total
                ORDER BY vs.ward_number
            ''',
            'description': 'Voter turnout calculated per ward'
        },
        'winners': {
            'sql': '''
                WITH race_results AS (
                    SELECT
                        r.race_id,
                        r.type AS race_type,
                        CASE 
                            WHEN r.type = 'MAYOR' THEN 'City-wide'
                            ELSE 'Ward ' || r.ward_number::text
                        END AS race_scope,
                        c.name AS candidate_name,
                        SUM(er.votes) AS total_votes,
                        RANK() OVER (PARTITION BY r.race_id ORDER BY SUM(er.votes) DESC) AS rank
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    GROUP BY r.race_id, r.type, r.ward_number, c.name
                )
                SELECT race_type, race_scope, candidate_name AS winner, total_votes
                FROM race_results
                WHERE rank = 1
                ORDER BY CASE race_type WHEN 'MAYOR' THEN 0 ELSE 1 END, race_scope
            ''',
            'description': 'Election winners (Mayor + 14 Councillors)'
        }
    }

    query_info = table_queries.get(selected_dataset)
    
    if not query_info:
        return (
            html.Pre("-- No query defined", className="small text-muted"),
            html.P("Select a dataset.", className="text-muted")
        )

    sql = query_info['sql']
    description = query_info['description']

    # Display query
    query_display = html.Div([
        html.P(description, className="text-muted mb-2"),
        html.Pre(sql.strip(), className="small bg-light p-2 rounded border")
    ])

    # Execute and display results
    try:
        df = query_db(sql)
        
        if df.empty:
            return query_display, html.Div([
                html.P("⚠️ Query returned no rows - table might be empty.", className="text-warning"),
                html.P("Run the ETL script:", className="text-muted small"),
                html.Pre("docker-compose exec app python app/load_data.py", className="small bg-light p-2")
            ])

        table = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=20,
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#007bff",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "left"
            },
            style_cell={
                "fontSize": 13,
                "fontFamily": "system-ui",
                "padding": "8px 12px",
                "textAlign": "left",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
            ],
        )

        row_count = html.P(f"Showing {len(df)} rows", className="text-muted small mt-2")
        return query_display, html.Div([table, row_count])

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        
        error_display = html.Div([
            html.H5("❌ Query Error", className="text-danger"),
            html.P(f"Error: {str(e)}", className="text-danger"),
            html.Details([
                html.Summary("Show full error", className="text-muted small"),
                html.Pre(error_detail, className="small bg-light p-2 border")
            ]),
            html.Hr(),
            html.P("Common issues:", className="fw-bold mt-3"),
            html.Ul([
                html.Li("Database is empty - run ETL script"),
                html.Li("Table name mismatch"),
                html.Li("Database connection lost"),
            ]),
            html.Pre(
                "# Load data:\ndocker-compose exec app python app/load_data.py\n\n# Check tables:\ndocker-compose exec db psql -U appuser -d calgary_ward_db -c \"\\dt\"",
                className="small bg-light p-2"
            )
        ])
        
        return query_display, error_display

if __name__ == "__main__":
    print("Dashboard started on http://0.0.0.0:8050")
    app.run(host="0.0.0.0", port=8050, debug=True)