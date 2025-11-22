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
                                                                    "label": "Turnout Rate by Ward Population",
                                                                    "value": "curated_population_turnout",
                                                                },
                                                                {
                                                                    "label": "Income Diversity and Voter Engagement",
                                                                    "value": "curated_income_diversity",
                                                                },
                                                                {
                                                                    "label": "Crime & Disorder vs Safety Perception",
                                                                    "value": "curated_safety_profile",
                                                                },
                                                                {
                                                                    "label": "Mayoral Race: Geographic Patterns",
                                                                    "value": "curated_mayoral_geography",
                                                                },
                                                                {
                                                                    "label": "Employment Rate vs Civic Engagement",
                                                                    "value": "curated_employment_engagement",
                                                                },
                                                                {
                                                                    "label": "Service Access & Quality of Life",
                                                                    "value": "curated_service_quality",
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
                                                # Core Reference Tables
                                                {'label': 'Ward', 'value': 'ward'},
                                                {'label': 'Election', 'value': 'election'},
                                                {'label': 'Race', 'value': 'race'},
                                                {'label': 'Candidate', 'value': 'candidate'},
                                                {'label': 'Candidacy', 'value': 'candidacy'},
                                                {'label': 'Voting Station', 'value': 'voting_station'},
                                                {'label': 'Election Result', 'value': 'election_result'},
                                                # Demographic Tables
                                                {'label': 'Population', 'value': 'ward_population'},
                                                {'label': 'Age & Gender', 'value': 'ward_age_gender'},
                                                {'label': 'Income', 'value': 'ward_income'},
                                                {'label': 'Education', 'value': 'ward_education'},
                                                {'label': 'Labour Force', 'value': 'ward_labour_force'},
                                                {'label': 'Transport Mode', 'value': 'ward_transport_mode'},
                                                # Service & Safety Tables
                                                {'label': 'Crime', 'value': 'ward_crime'},
                                                {'label': 'Disorder', 'value': 'ward_disorder'},
                                                {'label': 'Transit Stops', 'value': 'ward_transit_stops'},
                                                {'label': 'Recreation', 'value': 'ward_recreation'},
                                                {'label': 'Community Services', 'value': 'community_services'},
                                                # Calculated Views
                                                {'label': 'Voter Turnout (Calculated)', 'value': 'turnout'},
                                                {'label': 'Election Winners (Calculated)', 'value': 'winners'},
                                            ],
                                            value='ward',
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
    Input("selected-ward-store", "data"),
)
def update_ward_details(selected_ward):
    if not selected_ward or selected_ward.get("ward_number") is None:
        return html.P("Select a ward on the map to view details.", className="text-muted")

    ward_number = selected_ward["ward_number"]
    
    # Query ward details
    query = '''
        SELECT 
            w.ward_number,
            w.ward_name,
            wp.total as population,
            wc.rate_per_1000 as crime_rate,
            wd.rate_per_1000 as disorder_rate
        FROM ward w
        LEFT JOIN ward_population wp ON w.ward_number = wp.ward_number
        LEFT JOIN ward_crime wc ON w.ward_number = wc.ward_number
        LEFT JOIN ward_disorder wd ON w.ward_number = wd.ward_number
        WHERE w.ward_number = :ward_num
    '''
    
    try:
        df = query_db(query, params={'ward_num': ward_number})
        
        if df.empty:
            return html.P(f"No data available for Ward {ward_number}", className="text-warning")
        
        row = df.iloc[0]
        population = f"{row['population']:,}" if pd.notna(row['population']) else "N/A"
        crime_rate = f"{row['crime_rate']:.1f}" if pd.notna(row['crime_rate']) else "N/A"
        disorder_rate = f"{row['disorder_rate']:.1f}" if pd.notna(row['disorder_rate']) else "N/A"
        
        # Get turnout and winner
        turnout_query = '''
            SELECT
                ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
            FROM election_result er
            JOIN voting_station vs ON er.station_code = vs.station_code
            JOIN ward_population wp ON vs.ward_number = wp.ward_number
            JOIN race r ON er.race_id = r.race_id
            WHERE vs.ward_number = :ward_num AND r.type = 'MAYOR'
            GROUP BY wp.total
        '''
        
        winner_query = '''
            WITH ward_votes AS (
                SELECT
                    c.name,
                    SUM(er.votes) as total_votes
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                WHERE vs.ward_number = :ward_num AND r.type = 'MAYOR'
                GROUP BY c.name
                ORDER BY total_votes DESC
                LIMIT 1
            )
            SELECT name as winner FROM ward_votes
        '''
        
        turnout_df = query_db(turnout_query, params={'ward_num': ward_number})
        winner_df = query_db(winner_query, params={'ward_num': ward_number})
        
        turnout_rate = f"{turnout_df.iloc[0]['turnout_rate']}%" if not turnout_df.empty else "N/A"
        winner = winner_df.iloc[0]['winner'] if not winner_df.empty else "N/A"
        
        detail_children = [
            html.H5(f"Ward {ward_number}", className="mb-3"),
            make_metric_card("Population", population),
            make_metric_card("Turnout Rate", turnout_rate, "Mayoral race"),
            make_metric_card("Crime Rate", crime_rate, "Per 1,000 residents"),
            make_metric_card("Disorder Rate", disorder_rate, "Per 1,000 residents"),
            make_metric_card("Top Mayoral Candidate", winner, "Most votes in ward"),
        ]
        
        return detail_children
        
    except Exception as e:
        print(f"Error in ward details: {e}")
        return html.P(f"Error loading data for Ward {ward_number}", className="text-danger")



# ---- Curated Sets ----

@app.callback(
    Output("curated-viz-graph", "figure"),
    Output("curated-description", "children"),
    Input("curated-select", "value"),
)
def update_curated_visualization(curated_id):
    fig = go.Figure()

    if curated_id == "curated_population_turnout":
        # Query: Population vs Turnout Rate
        query = '''
            SELECT
                vs.ward_number,
                wp.total as population,
                SUM(er.votes) as total_votes,
                ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
            FROM election_result er
            JOIN voting_station vs ON er.station_code = vs.station_code
            JOIN ward_population wp ON vs.ward_number = wp.ward_number
            JOIN race r ON er.race_id = r.race_id
            WHERE r.type = 'MAYOR'
            GROUP BY vs.ward_number, wp.total
            ORDER BY wp.total
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df, 
            x='population', 
            y='turnout_rate',
            text='ward_number',
            title='Voter Turnout Rate by Ward Population',
            labels={'population': 'Ward Population', 'turnout_rate': 'Turnout Rate (%)'},
            size='total_votes',
            size_max=20
        )
        fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
        fig.update_layout(height=600, showlegend=False)
        
        desc = "Examines whether larger wards have different civic engagement patterns. Each bubble represents a ward, sized by total votes cast."

    elif curated_id == "curated_income_diversity":
        # Query: Income distribution spread vs turnout
        query = '''
            WITH income_stats AS (
                SELECT 
                    wi.ward_number,
                    SUM(wi.household_count) as total_households,
                    SUM(CASE WHEN wi.income_group IN ('Under $20,000', '$20,000 to $39,999') 
                        THEN wi.household_count ELSE 0 END) as low_income,
                    SUM(CASE WHEN wi.income_group IN ('$200,000 and over') 
                        THEN wi.household_count ELSE 0 END) as high_income
                FROM ward_income wi
                GROUP BY wi.ward_number
            ),
            turnout_stats AS (
                SELECT
                    vs.ward_number,
                    SUM(er.votes) as total_votes,
                    wp.total as population,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                i.ward_number,
                ROUND(100.0 * i.low_income / i.total_households, 1) as low_income_pct,
                ROUND(100.0 * i.high_income / i.total_households, 1) as high_income_pct,
                t.turnout_rate
            FROM income_stats i
            JOIN turnout_stats t ON i.ward_number = t.ward_number
            ORDER BY i.ward_number
        '''
        df = query_db(query)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['low_income_pct'],
            y=df['turnout_rate'],
            mode='markers+text',
            text=df['ward_number'],
            textposition='top center',
            name='Low Income vs Turnout',
            marker=dict(size=12, color='#FF6B6B')
        ))
        fig.add_trace(go.Scatter(
            x=df['high_income_pct'],
            y=df['turnout_rate'],
            mode='markers+text',
            text=df['ward_number'],
            textposition='bottom center',
            name='High Income vs Turnout',
            marker=dict(size=12, color='#4ECDC4')
        ))
        fig.update_layout(
            title='Income Levels and Voter Turnout',
            xaxis_title='Percentage of Households',
            yaxis_title='Turnout Rate (%)',
            height=600
        )
        
        desc = "Compares low-income households (under $40k) and high-income households ($200k+) against turnout rates. Red shows low-income correlation, teal shows high-income correlation."

    elif curated_id == "curated_safety_profile":
        # Query: Crime and disorder rates
        query = '''
            SELECT 
                wc.ward_number,
                wc.rate_per_1000 as crime_rate,
                wd.rate_per_1000 as disorder_rate,
                ROUND((wc.rate_per_1000 + wd.rate_per_1000) / 2, 1) as combined_safety_index
            FROM ward_crime wc
            JOIN ward_disorder wd ON wc.ward_number = wd.ward_number
            ORDER BY combined_safety_index DESC
        '''
        df = query_db(query)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['ward_number'],
            y=df['crime_rate'],
            name='Crime Rate',
            marker_color='#E74C3C'
        ))
        fig.add_trace(go.Bar(
            x=df['ward_number'],
            y=df['disorder_rate'],
            name='Disorder Rate',
            marker_color='#F39C12'
        ))
        fig.update_layout(
            title='Crime and Disorder Rates by Ward',
            xaxis_title='Ward Number',
            yaxis_title='Rate per 1,000 Residents',
            barmode='group',
            height=600
        )
        
        desc = "Shows crime and disorder rates across wards. Higher rates indicate greater public safety challenges. Wards 7, 8, 9, and 10 show significantly higher rates."

    elif curated_id == "curated_mayoral_geography":
        # Query: Top mayoral candidates by ward
        query = '''
            WITH candidate_votes AS (
                SELECT
                    vs.ward_number,
                    c.name as candidate_name,
                    SUM(er.votes) as votes
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, c.name
            ),
            top_candidates AS (
                SELECT DISTINCT candidate_name
                FROM candidate_votes
                GROUP BY candidate_name
                ORDER BY SUM(votes) DESC
                LIMIT 6
            )
            SELECT 
                cv.ward_number,
                cv.candidate_name,
                cv.votes
            FROM candidate_votes cv
            WHERE cv.candidate_name IN (SELECT candidate_name FROM top_candidates)
            ORDER BY cv.ward_number, cv.votes DESC
        '''
        df = query_db(query)
        
        fig = px.bar(
            df,
            x='ward_number',
            y='votes',
            color='candidate_name',
            title='Top 6 Mayoral Candidates: Vote Distribution by Ward',
            labels={'ward_number': 'Ward Number', 'votes': 'Votes', 'candidate_name': 'Candidate'},
            barmode='stack',
            height=600
        )
        fig.update_xaxis(dtick=1)
        
        desc = "Shows geographic patterns in mayoral candidate support. Each color represents one of the top 6 candidates, revealing which wards favored which candidates."

    elif curated_id == "curated_employment_engagement":
        # Query: Employment rate vs turnout
        query = '''
            WITH employment AS (
                SELECT 
                    ward_number,
                    AVG(employment_rate) as avg_employment_rate
                FROM ward_labour_force
                GROUP BY ward_number
            ),
            turnout AS (
                SELECT
                    vs.ward_number,
                    wp.total as population,
                    SUM(er.votes) as total_votes,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                e.ward_number,
                e.avg_employment_rate,
                t.turnout_rate
            FROM employment e
            JOIN turnout t ON e.ward_number = t.ward_number
            ORDER BY e.ward_number
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df,
            x='avg_employment_rate',
            y='turnout_rate',
            text='ward_number',
            title='Employment Rate vs Voter Turnout',
            labels={'avg_employment_rate': 'Employment Rate (%)', 'turnout_rate': 'Voter Turnout Rate (%)'},
            trendline='ols',
            height=600
        )
        fig.update_traces(textposition='top center', marker=dict(size=12))
        
        desc = "Explores whether wards with higher employment rates show different civic engagement levels. Includes trendline to show correlation."

    elif curated_id == "curated_service_quality":
        # Query: Services per capita vs population
        query = '''
            WITH service_counts AS (
                SELECT 
                    ward_number,
                    SUM(count) as total_services
                FROM community_services
                GROUP BY ward_number
            ),
            recreation_counts AS (
                SELECT 
                    ward_number,
                    SUM(count) as total_recreation
                FROM ward_recreation
                GROUP BY ward_number
            ),
            transit_counts AS (
                SELECT 
                    ward_number,
                    active as transit_stops
                FROM ward_transit_stops
            )
            SELECT 
                wp.ward_number,
                wp.total as population,
                COALESCE(sc.total_services, 0) as services,
                COALESCE(rc.total_recreation, 0) as recreation,
                COALESCE(tc.transit_stops, 0) as transit_stops,
                ROUND((COALESCE(sc.total_services, 0) + COALESCE(rc.total_recreation, 0)) * 1000.0 / wp.total, 2) as services_per_1000
            FROM ward_population wp
            LEFT JOIN service_counts sc ON wp.ward_number = sc.ward_number
            LEFT JOIN recreation_counts rc ON wp.ward_number = rc.ward_number
            LEFT JOIN transit_counts tc ON wp.ward_number = tc.ward_number
            ORDER BY services_per_1000 DESC
        '''
        df = query_db(query)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['ward_number'],
            y=df['services'],
            name='Community Services',
            marker_color='#3498DB'
        ))
        fig.add_trace(go.Bar(
            x=df['ward_number'],
            y=df['recreation'],
            name='Recreation Facilities',
            marker_color='#2ECC71'
        ))
        fig.update_layout(
            title='Service and Recreation Facility Distribution by Ward',
            xaxis_title='Ward Number',
            yaxis_title='Number of Facilities',
            barmode='stack',
            height=600
        )
        
        desc = "Compares community services and recreation facilities across wards. Reveals which wards have better access to public amenities and quality of life infrastructure."

    else:
        fig.update_layout(title="Select a curated visualization")
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
        # Core Reference Tables
        'ward': {
            'sql': 'SELECT * FROM ward ORDER BY ward_number',
            'description': 'All Calgary wards (1-14)'
        },
        'election': {
            'sql': 'SELECT * FROM election ORDER BY election_date DESC',
            'description': 'Election events'
        },
        'race': {
            'sql': '''
                SELECT 
                    r.race_id,
                    e.year,
                    r.type,
                    r.ward_number,
                    CASE 
                        WHEN r.type = 'MAYOR' THEN 'City-wide'
                        ELSE 'Ward ' || r.ward_number::text
                    END as scope
                FROM race r
                JOIN election e ON r.election_id = e.election_id
                ORDER BY e.year DESC, r.type, r.ward_number
            ''',
            'description': 'Election races (Mayor + Councillor by ward)'
        },
        'candidate': {
            'sql': 'SELECT * FROM candidate ORDER BY name',
            'description': 'All candidates'
        },
        'candidacy': {
            'sql': '''
                SELECT 
                    c.name as candidate_name,
                    r.type as race_type,
                    CASE 
                        WHEN r.type = 'MAYOR' THEN 'City-wide'
                        ELSE 'Ward ' || r.ward_number::text
                    END as race_scope,
                    e.year
                FROM candidacy cy
                JOIN candidate c ON cy.candidate_id = c.candidate_id
                JOIN race r ON cy.race_id = r.race_id
                JOIN election e ON r.election_id = e.election_id
                ORDER BY e.year DESC, r.type, r.ward_number, c.name
            ''',
            'description': 'Candidate participation in races'
        },
        'voting_station': {
            'sql': 'SELECT * FROM voting_station ORDER BY ward_number, station_code',
            'description': 'Physical voting locations by ward'
        },
        'election_result': {
            'sql': '''
                SELECT 
                    er.station_code,
                    vs.ward_number,
                    c.name as candidate_name,
                    r.type as race_type,
                    er.votes
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                ORDER BY vs.ward_number, er.station_code, er.votes DESC
                LIMIT 200
            ''',
            'description': 'Raw election results by voting station (showing first 200 of ~47,000 rows)'
        },
        
        # Demographic Tables
        'ward_population': {
            'sql': 'SELECT * FROM ward_population ORDER BY ward_number',
            'description': 'Population statistics by ward'
        },
        'ward_age_gender': {
            'sql': 'SELECT * FROM ward_age_gender ORDER BY ward_number, age_group',
            'description': 'Population by age group and gender'
        },
        'ward_income': {
            'sql': 'SELECT * FROM ward_income ORDER BY ward_number, income_group',
            'description': 'Household income distribution by ward'
        },
        'ward_education': {
            'sql': 'SELECT * FROM ward_education ORDER BY ward_number, education_level',
            'description': 'Education levels by ward'
        },
        'ward_labour_force': {
            'sql': 'SELECT * FROM ward_labour_force ORDER BY ward_number, gender',
            'description': 'Labour force statistics by ward and gender'
        },
        'ward_transport_mode': {
            'sql': 'SELECT * FROM ward_transport_mode ORDER BY ward_number, transport_mode',
            'description': 'Commute modes to work by ward'
        },
        
        # Service & Safety Tables
        'ward_crime': {
            'sql': 'SELECT * FROM ward_crime ORDER BY ward_number',
            'description': 'Crime statistics by ward'
        },
        'ward_disorder': {
            'sql': 'SELECT * FROM ward_disorder ORDER BY ward_number',
            'description': 'Disorder incidents by ward'
        },
        'ward_transit_stops': {
            'sql': 'SELECT * FROM ward_transit_stops ORDER BY ward_number',
            'description': 'Public transit stop counts by ward'
        },
        'ward_recreation': {
            'sql': 'SELECT * FROM ward_recreation ORDER BY ward_number, facility_type',
            'description': 'Recreation facilities by type and ward'
        },
        'community_services': {
            'sql': 'SELECT * FROM community_services ORDER BY ward_number, service_type',
            'description': 'Community service facilities by ward'
        },
        
        # Calculated Views
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
                html.P("Query returned no rows - table might be empty.", className="text-warning"),
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
            html.H5("Query Error", className="text-danger"),
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