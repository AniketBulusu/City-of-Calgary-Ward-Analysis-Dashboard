from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"

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

age_sex_df = load_csv("_Ward_Age_Sex.csv")
community_services_df = load_csv("_Ward_Community_Services.csv")
crime_df = load_csv("_Ward_Crime.csv")
disorder_df = load_csv("_Ward_Disorder.csv")
education_df = load_csv("_Ward_Education.csv")
election_result_df = load_csv("_Ward_Election_Result.csv")
income_df = load_csv("_Ward_Household_Income.csv")
labour_df = load_csv("_Ward_Labour_Force.csv")
population_df = load_csv("_Ward_Population.csv")
recreation_df = load_csv("_Ward_Rec_Facilities.csv")
transit_stops_df = load_csv("_Ward_Transit_Stops.csv")
work_transport_df = load_csv("_Ward_Work_Transport.csv")

CHARACTERISTIC_OPTIONS = [

]

ELECTION_OPTIONS = [
    {"label" : "Turnout", "value" : "turnout"}
    {"label" : "Winner", "value" : "winner"}
]