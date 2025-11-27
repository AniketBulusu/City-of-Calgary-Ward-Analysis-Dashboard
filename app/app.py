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
from map_component import ward_map_component  # ← Import your custom map

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
                        dbc.Row([
                            dbc.Col([
                                html.H4("Calgary Ward Map", className="mt-3 mb-2"),
                                html.P(
                                    "Hover over a ward to see councillor, population, turnout, crime, disorder, and community services data.",
                                    className="text-muted",
                                ),
                                ward_map_component(),
                            ], width=12),
                        ])
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
                                                                    "label": "Quality of Life Index vs Turnout",
                                                                    "value": "curated_qol_turnout",
                                                                },
                                                                {
                                                                    "label": "Candidate Appeal by Age Demographics",
                                                                    "value": "curated_age_candidates",
                                                                },
                                                                {
                                                                    "label": "Education-Employment-Voting Triangle",
                                                                    "value": "curated_edu_employ_triangle",
                                                                },
                                                                {
                                                                    "label": "Voting Accessibility Impact",
                                                                    "value": "curated_accessibility",
                                                                },
                                                                {
                                                                    "label": "Voting Station Anomalies",
                                                                    "value": "curated_anomalies",
                                                                },
                                                            ],
                                                            value="curated_qol_turnout",
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
                                                        "on-demand using SQL queries, pandas, Plotly, and Dash.",
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

                                dbc.Col(
                                    [
                                        html.H4(
                                            "Disclaimer on Data",
                                            className="mt-4 mb-3",
                                        ),
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "The original data sources for this project only included "
                                                        "binary gender categories of male and female. We recognize "
                                                        "that these statistics contain "
                                                        "important information regarding political leanings and - more "
                                                        "generally - social importance. The decision was made to model "
                                                        "the data that exists for the sake of the project as is. "
                                                        "This limitation reduces inclusiveness and should "
                                                        "be considered when interpreting.",
                                                        className="mb-2",
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

# ---- Curated Sets ----

@app.callback(
    Output("curated-viz-graph", "figure"),
    Output("curated-description", "children"),
    Input("curated-select", "value"),
)
def update_curated_visualization(curated_id):
    fig = go.Figure()

    if curated_id == "curated_qol_turnout":
        # Quality of Life Index vs Turnout
        query = '''
            WITH qol_metrics AS (
                SELECT 
                    w.ward_number,
                    wp.total as population,
                    -- Services per 1000 residents (positive)
                    COALESCE(cs.total_services, 0) * 1000.0 / wp.total as services_score,
                    -- Recreation per 1000 residents (positive)
                    COALESCE(rec.total_recreation, 0) * 1000.0 / wp.total as recreation_score,
                    -- Transit stops per 1000 residents (positive)
                    wts.active * 1000.0 / wp.total as transit_score,
                    -- Safety: inverse of crime+disorder (negative becomes positive)
                    100 - (wc.rate_per_1000 + wd.rate_per_1000) as safety_score
                FROM ward w
                JOIN ward_population wp ON w.ward_number = wp.ward_number
                LEFT JOIN (SELECT ward_number, SUM(count) as total_services FROM community_services GROUP BY ward_number) cs 
                    ON w.ward_number = cs.ward_number
                LEFT JOIN (SELECT ward_number, SUM(count) as total_recreation FROM ward_recreation GROUP BY ward_number) rec 
                    ON w.ward_number = rec.ward_number
                LEFT JOIN ward_transit_stops wts ON w.ward_number = wts.ward_number
                LEFT JOIN ward_crime wc ON w.ward_number = wc.ward_number
                LEFT JOIN ward_disorder wd ON w.ward_number = wd.ward_number
            ),
            turnout AS (
                SELECT
                    vs.ward_number,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                q.ward_number,
                -- Composite QoL index (weighted average, normalized)
                ROUND((q.services_score * 2 + q.recreation_score * 2 + q.transit_score + q.safety_score) / 6, 1) as qol_index,
                t.turnout_rate
            FROM qol_metrics q
            JOIN turnout t ON q.ward_number = t.ward_number
            ORDER BY q.ward_number
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df,
            x='qol_index',
            y='turnout_rate',
            text='ward_number',
            title='Quality of Life Index vs Voter Turnout',
            labels={'qol_index': 'Quality of Life Index', 'turnout_rate': 'Voter Turnout Rate (%)'},
            trendline='ols',
            height=600
        )
        fig.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=1, color='white')))
        
        desc = "Tests whether wards with better quality of life see higher civic engagement. QoL index combines community services, recreation facilities, transit accessibility, and safety (inverse of crime/disorder). Trendline shows correlation strength."

    elif curated_id == "curated_age_candidates":
        # Candidate Appeal by Age Demographics
        query = '''
            WITH age_profiles AS (
                SELECT 
                    ward_number,
                    -- Youth index: % population aged 20-39
                    ROUND(100.0 * SUM(CASE WHEN age_group IN ('20-24', '25-29', '30-34', '35-39') 
                                          THEN total ELSE 0 END) / 
                          NULLIF(MAX(CASE WHEN age_group = 'Total' THEN total END), 0), 1) as youth_index,
                    -- Senior index: % population aged 60+
                    ROUND(100.0 * SUM(CASE WHEN age_group IN ('60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100 years and over') 
                                          THEN total ELSE 0 END) / 
                          NULLIF(MAX(CASE WHEN age_group = 'Total' THEN total END), 0), 1) as senior_index
                FROM ward_age_gender
                GROUP BY ward_number
            ),
            ward_winners AS (
                SELECT 
                    vs.ward_number,
                    c.name as top_candidate,
                    SUM(er.votes) as candidate_votes,
                    RANK() OVER (PARTITION BY vs.ward_number ORDER BY SUM(er.votes) DESC) as rank
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, c.name
            ),
            turnout AS (
                SELECT
                    vs.ward_number,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 1) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                ap.ward_number,
                ap.youth_index,
                ap.senior_index,
                ww.top_candidate,
                t.turnout_rate
            FROM age_profiles ap
            JOIN ward_winners ww ON ap.ward_number = ww.ward_number AND ww.rank = 1
            JOIN turnout t ON ap.ward_number = t.ward_number
            ORDER BY ap.ward_number
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df,
            x='youth_index',
            y='senior_index',
            text='ward_number',
            color='top_candidate',
            size='turnout_rate',
            title='Age Demographics and Mayoral Candidate Appeal',
            labels={'youth_index': 'Youth Index (% aged 20-39)', 
                   'senior_index': 'Senior Index (% aged 60+)',
                   'top_candidate': 'Top Candidate'},
            height=600
        )
        fig.update_traces(textposition='top center')
        
        desc = "Maps wards by age demographics and shows which mayoral candidate won each. Youth index = % aged 20-39, Senior index = % aged 60+. Bubble size = turnout rate. Reveals whether certain candidates appealed more to younger vs older communities."

    elif curated_id == "curated_edu_employ_triangle":
        # Education-Employment-Voting Triangle
        query = '''
            WITH education AS (
                SELECT 
                    ward_number,
                    MAX(CASE WHEN education_level = 'Post Secondary' THEN percent END) as postsecondary_pct
                FROM ward_education
                GROUP BY ward_number
            ),
            employment AS (
                SELECT 
                    ward_number,
                    AVG(employment_rate) as avg_employment_rate
                FROM ward_labour_force
                GROUP BY ward_number
            ),
            winners AS (
                SELECT 
                    vs.ward_number,
                    c.name as winning_candidate,
                    RANK() OVER (PARTITION BY vs.ward_number ORDER BY SUM(er.votes) DESC) as rank
                FROM election_result er
                JOIN candidate c ON er.candidate_id = c.candidate_id
                JOIN race r ON er.race_id = r.race_id
                JOIN voting_station vs ON er.station_code = vs.station_code
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, c.name
            ),
            turnout AS (
                SELECT
                    vs.ward_number,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 1) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                ed.ward_number,
                ed.postsecondary_pct as education_pct,
                em.avg_employment_rate as employment_rate,
                w.winning_candidate,
                t.turnout_rate
            FROM education ed
            JOIN employment em ON ed.ward_number = em.ward_number
            JOIN winners w ON ed.ward_number = w.ward_number AND w.rank = 1
            JOIN turnout t ON ed.ward_number = t.ward_number
            ORDER BY ed.ward_number
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df,
            x='employment_rate',
            y='education_pct',
            text='ward_number',
            color='winning_candidate',
            size='turnout_rate',
            title='Education-Employment-Voting Triangle',
            labels={'employment_rate': 'Employment Rate (%)', 
                   'education_pct': 'Post-Secondary Education (%)',
                   'winning_candidate': 'Winning Candidate'},
            height=600
        )
        fig.update_traces(textposition='top center')
        
        desc = "Three-dimensional analysis: employment rate (x-axis), education level (y-axis), colored by winning mayoral candidate, sized by turnout. Shows whether educated-employed wards cluster around certain candidates, revealing socioeconomic voting patterns."

    elif curated_id == "curated_accessibility":
        # Voting Accessibility Impact
        query = '''
            WITH station_density AS (
                SELECT 
                    vs.ward_number,
                    COUNT(*) as num_stations,
                    wp.total as population,
                    ROUND(COUNT(*) * 10000.0 / wp.total, 2) as stations_per_10k
                FROM voting_station vs
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                GROUP BY vs.ward_number, wp.total
            ),
            turnout AS (
                SELECT
                    vs.ward_number,
                    ROUND(100.0 * SUM(er.votes)::numeric / wp.total, 2) as turnout_rate
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN ward_population wp ON vs.ward_number = wp.ward_number
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY vs.ward_number, wp.total
            )
            SELECT 
                sd.ward_number,
                sd.num_stations,
                sd.stations_per_10k,
                t.turnout_rate
            FROM station_density sd
            JOIN turnout t ON sd.ward_number = t.ward_number
            ORDER BY sd.ward_number
        '''
        df = query_db(query)
        
        fig = px.scatter(
            df,
            x='stations_per_10k',
            y='turnout_rate',
            text='ward_number',
            title='Voting Accessibility Impact on Turnout',
            labels={'stations_per_10k': 'Voting Stations per 10,000 Residents', 
                   'turnout_rate': 'Voter Turnout Rate (%)'},
            size='num_stations',
            trendline='ols',
            height=600
        )
        fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
        
        desc = "Tests whether voting convenience affects turnout. Measures voting station density (stations per 10,000 residents) against turnout rate. Bubble size = absolute number of stations. Trendline shows if more accessible voting correlates with higher participation."

    elif curated_id == "curated_anomalies":
        # Voting Station Anomalies
        query = '''
            WITH station_turnout AS (
                SELECT 
                    er.station_code,
                    vs.ward_number,
                    vs.station_name,
                    SUM(er.votes) as station_votes
                FROM election_result er
                JOIN voting_station vs ON er.station_code = vs.station_code
                JOIN race r ON er.race_id = r.race_id
                WHERE r.type = 'MAYOR'
                GROUP BY er.station_code, vs.ward_number, vs.station_name
            ),
            ward_avg AS (
                SELECT 
                    vs.ward_number,
                    AVG(station_votes) as ward_avg_votes,
                    STDDEV(station_votes) as ward_stddev
                FROM station_turnout st
                JOIN voting_station vs ON st.station_code = vs.station_code
                GROUP BY vs.ward_number
            )
            SELECT 
                st.station_code,
                st.ward_number,
                st.station_name,
                st.station_votes,
                wa.ward_avg_votes,
                ROUND((st.station_votes - wa.ward_avg_votes) / NULLIF(wa.ward_stddev, 0), 2) as z_score
            FROM station_turnout st
            JOIN ward_avg wa ON st.ward_number = wa.ward_number
            WHERE ABS((st.station_votes - wa.ward_avg_votes) / NULLIF(wa.ward_stddev, 0)) > 1.5
            ORDER BY ABS((st.station_votes - wa.ward_avg_votes) / NULLIF(wa.ward_stddev, 0)) DESC
            LIMIT 20
        '''
        df = query_db(query)
        
        fig = go.Figure()
        
        colors = ['#E74C3C' if z < 0 else '#2ECC71' for z in df['z_score']]
        
        fig.add_trace(go.Bar(
            x=df['z_score'],
            y=[f"Ward {row['ward_number']}: {row['station_name'][:30]}" for _, row in df.iterrows()],
            orientation='h',
            marker=dict(color=colors),
            text=df['station_votes'],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Voting Station Anomalies (Top 20 by Z-Score)',
            xaxis_title='Z-Score (Standard Deviations from Ward Average)',
            yaxis_title='Voting Station',
            height=600,
            showlegend=False
        )
        
        desc = "Identifies voting stations with unusual turnout compared to their ward average. Z-score measures how many standard deviations a station differs from its ward's average. Green = unusually high turnout, Red = unusually low. Reveals location-specific factors affecting participation."

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

    try:
        # POPULATION
        if characteristic == "population" and politics == "turnout":
            query = '''
                SELECT
                    wp.ward_number,
                    wp.total as population,
                    SUM(er.votes) AS total_votes
                FROM ward_population wp
                LEFT JOIN voting_station vs ON wp.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY wp.ward_number, wp.total
                ORDER BY wp.ward_number
            '''
            df = query_db(query)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['ward_number'], y=df['population'], name='Population', marker_color='skyblue'))
            fig.add_trace(go.Bar(x=df['ward_number'], y=df['total_votes'], name='Total Votes', marker_color='salmon'))
            fig.update_layout(
                title='Population vs Voter Turnout by Ward',
                xaxis_title='Ward Number',
                yaxis_title='Count',
                barmode='group',
                height=600
            )
            msg = "Comparing ward population to actual voter turnout. Shows whether larger wards have proportionally higher turnout."

        elif characteristic == "population" and politics == "winner":
            query = '''
                WITH ward_votes AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT * FROM ward_votes ORDER BY ward_number, total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.bar(
                df,
                x='ward_number',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidate Performance by Ward',
                labels={'ward_number': 'Ward', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows which mayoral candidates received votes in each ward, stacked to show total turnout."

        # CRIME
        elif characteristic == "crime" and politics == "turnout":
            query = '''
                SELECT
                    wc.ward_number,
                    wc.rate_per_1000 as crime_rate,
                    SUM(er.votes) as total_votes
                FROM ward_crime wc
                LEFT JOIN voting_station vs ON wc.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY wc.ward_number, wc.rate_per_1000
                ORDER BY wc.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='crime_rate',
                y='total_votes',
                text='ward_number',
                title='Crime Rate vs Voter Turnout',
                labels={'crime_rate': 'Crime Rate (per 1,000 residents)', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Tests if higher crime rates correlate with lower voter turnout. Trendline shows relationship strength."

        elif characteristic == "crime" and politics == "winner":
            query = '''
                WITH ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    wc.rate_per_1000 as crime_rate,
                    ww.total_votes
                FROM ward_winners ww
                JOIN ward_crime wc ON ww.ward_number = wc.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='crime_rate',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidate Performance vs Crime Rate',
                labels={'crime_rate': 'Crime Rate (per 1,000)', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows which candidates performed better in high vs low crime wards."

        # DISORDER
        elif characteristic == "disorder" and politics == "turnout":
            query = '''
                SELECT
                    wd.ward_number,
                    wd.rate_per_1000 as disorder_rate,
                    SUM(er.votes) as total_votes
                FROM ward_disorder wd
                LEFT JOIN voting_station vs ON wd.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY wd.ward_number, wd.rate_per_1000
                ORDER BY wd.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='disorder_rate',
                y='total_votes',
                text='ward_number',
                title='Disorder Rate vs Voter Turnout',
                labels={'disorder_rate': 'Disorder Rate (per 1,000 residents)', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Analyzes if disorder incidents affect civic engagement and voter participation."

        elif characteristic == "disorder" and politics == "winner":
            query = '''
                WITH ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    wd.rate_per_1000 as disorder_rate,
                    ww.total_votes
                FROM ward_winners ww
                JOIN ward_disorder wd ON ww.ward_number = wd.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='disorder_rate',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidate Performance vs Disorder Rate',
                labels={'disorder_rate': 'Disorder Rate (per 1,000)', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Reveals which candidates appealed to wards with different disorder levels."

        # LABOUR FORCE
        elif characteristic == "labour" and politics == "turnout":
            query = '''
                WITH labour_summary AS (
                    SELECT 
                        ward_number,
                        AVG(employment_rate) as avg_employment_rate,
                        SUM(in_labour_force) as total_labour_force
                    FROM ward_labour_force
                    GROUP BY ward_number
                )
                SELECT
                    ls.ward_number,
                    ls.total_labour_force,
                    ls.avg_employment_rate,
                    SUM(er.votes) as total_votes
                FROM labour_summary ls
                LEFT JOIN voting_station vs ON ls.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY ls.ward_number, ls.total_labour_force, ls.avg_employment_rate
                ORDER BY ls.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_labour_force',
                y='total_votes',
                text='ward_number',
                size='avg_employment_rate',
                title='Labour Force Size vs Voter Turnout',
                labels={'total_labour_force': 'Total Labour Force', 'total_votes': 'Total Votes', 
                       'avg_employment_rate': 'Avg Employment Rate'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center')
            msg = "Tests if economically active wards have higher voter participation. Bubble size = employment rate."

        elif characteristic == "labour" and politics == "winner":
            query = '''
                WITH labour_summary AS (
                    SELECT 
                        ward_number,
                        SUM(in_labour_force) as total_labour_force
                    FROM ward_labour_force
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    ls.total_labour_force,
                    ww.total_votes
                FROM ward_winners ww
                JOIN labour_summary ls ON ww.ward_number = ls.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_labour_force',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidates vs Labour Force Size',
                labels={'total_labour_force': 'Labour Force', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows which candidates performed better in economically active wards."

        # EDUCATION
        elif characteristic == "education" and politics == "turnout":
            query = '''
                WITH education_summary AS (
                    SELECT 
                        ward_number,
                        MAX(CASE WHEN education_level = 'Post Secondary' THEN percent END) as postsecondary_pct
                    FROM ward_education
                    GROUP BY ward_number
                )
                SELECT
                    es.ward_number,
                    es.postsecondary_pct,
                    SUM(er.votes) as total_votes
                FROM education_summary es
                LEFT JOIN voting_station vs ON es.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY es.ward_number, es.postsecondary_pct
                ORDER BY es.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='postsecondary_pct',
                y='total_votes',
                text='ward_number',
                title='Post-Secondary Education vs Voter Turnout',
                labels={'postsecondary_pct': 'Post-Secondary Education (%)', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Tests if more educated wards have higher voter participation rates."

        elif characteristic == "education" and politics == "winner":
            query = '''
                WITH education_summary AS (
                    SELECT 
                        ward_number,
                        MAX(CASE WHEN education_level = 'Post Secondary' THEN percent END) as postsecondary_pct
                    FROM ward_education
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    es.postsecondary_pct,
                    ww.total_votes
                FROM ward_winners ww
                JOIN education_summary es ON ww.ward_number = es.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='postsecondary_pct',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidates vs Education Level',
                labels={'postsecondary_pct': 'Post-Secondary %', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Reveals which candidates appealed more to educated vs less educated wards."

        # INCOME
        elif characteristic == "income" and politics == "turnout":
            query = '''
                WITH income_summary AS (
                    SELECT 
                        ward_number,
                        SUM(household_count) as total_households,
                        -- Calculate weighted average income
                        ROUND(
                            (SUM(CASE WHEN income_group = 'under_$20000' THEN household_count * 10000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$20000_to_$39999' THEN household_count * 30000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$40000_to_$59999' THEN household_count * 50000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$60000_to_$79999' THEN household_count * 70000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$80000_to_$99999' THEN household_count * 90000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$100000_to_$124999' THEN household_count * 112500 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$125000_to_$149999' THEN household_count * 137500 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$150000_to_$199999' THEN household_count * 175000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$200000_and_over' THEN household_count * 250000 ELSE 0 END))
                            / NULLIF(SUM(household_count), 0)
                        ) as avg_income
                    FROM ward_income
                    GROUP BY ward_number
                )
                SELECT
                    ims.ward_number,
                    ims.avg_income,
                    SUM(er.votes) as total_votes
                FROM income_summary ims
                LEFT JOIN voting_station vs ON ims.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY ims.ward_number, ims.avg_income
                ORDER BY ims.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='avg_income',
                y='total_votes',
                text='ward_number',
                title='Average Household Income vs Voter Turnout',
                labels={'avg_income': 'Average Household Income ($)', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Tests if wealthier wards have higher voter participation. Income calculated as weighted average."

        elif characteristic == "income" and politics == "winner":
            query = '''
                WITH income_summary AS (
                    SELECT 
                        ward_number,
                        ROUND(
                            (SUM(CASE WHEN income_group = 'under_$20000' THEN household_count * 10000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$20000_to_$39999' THEN household_count * 30000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$40000_to_$59999' THEN household_count * 50000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$60000_to_$79999' THEN household_count * 70000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$80000_to_$99999' THEN household_count * 90000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$100000_to_$124999' THEN household_count * 112500 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$125000_to_$149999' THEN household_count * 137500 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$150000_to_$199999' THEN household_count * 175000 ELSE 0 END) +
                             SUM(CASE WHEN income_group = '$200000_and_over' THEN household_count * 250000 ELSE 0 END))
                            / NULLIF(SUM(household_count), 0)
                        ) as avg_income
                    FROM ward_income
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    ims.avg_income,
                    ww.total_votes
                FROM ward_winners ww
                JOIN income_summary ims ON ww.ward_number = ims.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            # Get top 5 candidates by total votes
            top_candidates = df.groupby('candidate_name')['total_votes'].sum().nlargest(5).index
            df_filtered = df[df['candidate_name'].isin(top_candidates)]
            
            fig = px.scatter(
                df_filtered,
                x='avg_income',
                y='total_votes',
                color='candidate_name',
                title='Top 5 Mayoral Candidates vs Household Income',
                labels={'avg_income': 'Average Income ($)', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows which candidates appealed to lower vs higher income wards (top 5 candidates only)."

        # COMMUNITY SERVICES
        elif characteristic == "services" and politics == "turnout":
            query = '''
                WITH services_summary AS (
                    SELECT 
                        ward_number,
                        SUM(count) as total_services
                    FROM community_services
                    GROUP BY ward_number
                )
                SELECT
                    ss.ward_number,
                    ss.total_services,
                    SUM(er.votes) as total_votes
                FROM services_summary ss
                LEFT JOIN voting_station vs ON ss.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY ss.ward_number, ss.total_services
                ORDER BY ss.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_services',
                y='total_votes',
                text='ward_number',
                size='total_services',
                title='Community Services vs Voter Turnout',
                labels={'total_services': 'Number of Community Services', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center')
            msg = "Tests if wards with more community services have higher civic engagement."

        elif characteristic == "services" and politics == "winner":
            query = '''
                WITH services_summary AS (
                    SELECT 
                        ward_number,
                        SUM(count) as total_services
                    FROM community_services
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    ss.total_services,
                    ww.total_votes
                FROM ward_winners ww
                JOIN services_summary ss ON ww.ward_number = ss.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_services',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidates vs Community Services',
                labels={'total_services': 'Community Services', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Reveals which candidates performed better in service-rich vs service-poor wards."

        # RECREATION
        elif characteristic == "recreation" and politics == "turnout":
            query = '''
                WITH rec_summary AS (
                    SELECT 
                        ward_number,
                        SUM(count) as total_recreation
                    FROM ward_recreation
                    GROUP BY ward_number
                )
                SELECT
                    rs.ward_number,
                    rs.total_recreation,
                    SUM(er.votes) as total_votes
                FROM rec_summary rs
                LEFT JOIN voting_station vs ON rs.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY rs.ward_number, rs.total_recreation
                ORDER BY rs.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_recreation',
                y='total_votes',
                text='ward_number',
                size='total_recreation',
                title='Recreation Facilities vs Voter Turnout',
                labels={'total_recreation': 'Number of Recreation Facilities', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center')
            msg = "Tests if wards with more recreation facilities have higher voter participation."

        elif characteristic == "recreation" and politics == "winner":
            query = '''
                WITH rec_summary AS (
                    SELECT 
                        ward_number,
                        SUM(count) as total_recreation
                    FROM ward_recreation
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    rs.total_recreation,
                    ww.total_votes
                FROM ward_winners ww
                JOIN rec_summary rs ON ww.ward_number = rs.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='total_recreation',
                y='total_votes',
                color='candidate_name',
                title='Mayoral Candidates vs Recreation Facilities',
                labels={'total_recreation': 'Recreation Facilities', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows which candidates appealed to wards with different recreation amenity levels."

        # TRANSIT STOPS
        elif characteristic == "transit" and politics == "turnout":
            query = '''
                SELECT
                    wts.ward_number,
                    wts.active as active_stops,
                    SUM(er.votes) as total_votes
                FROM ward_transit_stops wts
                LEFT JOIN voting_station vs ON wts.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY wts.ward_number, wts.active
                ORDER BY wts.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='active_stops',
                y='total_votes',
                text='ward_number',
                title='Active Transit Stops vs Voter Turnout',
                labels={'active_stops': 'Number of Active Transit Stops', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Tests if better transit access correlates with higher voter participation."

        elif characteristic == "transit" and politics == "winner":
            query = '''
                WITH ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    wts.active as active_stops,
                    ww.total_votes
                FROM ward_winners ww
                JOIN ward_transit_stops wts ON ww.ward_number = wts.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            # Get top 5 candidates
            top_candidates = df.groupby('candidate_name')['total_votes'].sum().nlargest(5).index
            df_filtered = df[df['candidate_name'].isin(top_candidates)]
            
            fig = px.line(
                df_filtered,
                x='active_stops',
                y='total_votes',
                color='candidate_name',
                markers=True,
                title='Top 5 Mayoral Candidates vs Transit Accessibility',
                labels={'active_stops': 'Active Transit Stops', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Shows how top 5 candidates performed in wards with different transit access levels."

        # PUBLIC TRANSIT USERS
        elif characteristic == "work_transit" and politics == "turnout":
            query = '''
                WITH transit_users AS (
                    SELECT 
                        ward_number,
                        SUM(CASE WHEN transport_mode = 'Public transit' THEN count ELSE 0 END) as transit_commuters
                    FROM ward_transport_mode
                    GROUP BY ward_number
                )
                SELECT
                    tu.ward_number,
                    tu.transit_commuters,
                    SUM(er.votes) as total_votes
                FROM transit_users tu
                LEFT JOIN voting_station vs ON tu.ward_number = vs.ward_number
                LEFT JOIN election_result er ON vs.station_code = er.station_code
                GROUP BY tu.ward_number, tu.transit_commuters
                ORDER BY tu.ward_number
            '''
            df = query_db(query)
            
            fig = px.scatter(
                df,
                x='transit_commuters',
                y='total_votes',
                text='ward_number',
                title='Public Transit Commuters vs Voter Turnout',
                labels={'transit_commuters': 'Number of Public Transit Commuters', 'total_votes': 'Total Votes'},
                trendline='ols',
                height=600
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            msg = "Tests if wards with more public transit users have higher voter turnout."

        elif characteristic == "work_transit" and politics == "winner":
            query = '''
                WITH transit_users AS (
                    SELECT 
                        ward_number,
                        SUM(CASE WHEN transport_mode = 'Public transit' THEN count ELSE 0 END) as transit_commuters
                    FROM ward_transport_mode
                    GROUP BY ward_number
                ),
                ward_winners AS (
                    SELECT
                        vs.ward_number,
                        c.name as candidate_name,
                        SUM(er.votes) as total_votes
                    FROM election_result er
                    JOIN candidate c ON er.candidate_id = c.candidate_id
                    JOIN race r ON er.race_id = r.race_id
                    JOIN voting_station vs ON er.station_code = vs.station_code
                    WHERE r.type = 'MAYOR'
                    GROUP BY vs.ward_number, c.name
                )
                SELECT 
                    ww.ward_number,
                    ww.candidate_name,
                    tu.transit_commuters,
                    ww.total_votes
                FROM ward_winners ww
                JOIN transit_users tu ON ww.ward_number = tu.ward_number
                ORDER BY ww.ward_number, ww.total_votes DESC
            '''
            df = query_db(query)
            
            # Get top 5 candidates
            top_candidates = df.groupby('candidate_name')['total_votes'].sum().nlargest(5).index
            df_filtered = df[df['candidate_name'].isin(top_candidates)]
            
            fig = px.scatter(
                df_filtered,
                x='transit_commuters',
                y='total_votes',
                color='candidate_name',
                title='Top 5 Mayoral Candidates vs Public Transit Usage',
                labels={'transit_commuters': 'Public Transit Commuters', 'total_votes': 'Votes', 'candidate_name': 'Candidate'},
                height=600
            )
            msg = "Reveals which candidates appealed to transit-dependent vs car-dependent wards."

        else:
            fig.update_layout(title="Unsupported combination")
            msg = "This characteristic-politics combination is not yet implemented."

    except Exception as e:
        print(f"Error in custom visualization: {e}")
        import traceback
        traceback.print_exc()
        fig.update_layout(title="Error generating visualization")
        msg = f"Error: {str(e)}"

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