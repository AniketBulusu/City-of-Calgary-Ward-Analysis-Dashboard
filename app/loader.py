## Loads data from the csv's into PostgreSQL database using the provided schema

import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine
from pathlib import Path
import sys

## FOR DOCKER

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://appuser:app_password@localhost:5432/calgary_ward_db"
    )

DATA_DIR = Path("/app/datasets")

################################################# UTILITIES #############################################

# connection to db
def get_engine():
    retry = 5
    delay = 3

    for attempt in range(retry):
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print('Connected to database.')
            return engine
        except Exception as e:
            if attempt < retry - 1:
                print("Waiting for DB... (attempt {attempt + 1}/{retry})")
                time.sleep(delay)
            else:
                print("Database connection failed after {retry} attempts: {e}")
                raise

# data standardiser
def load_data(filename):
    df = pd.read_csv(DATA_DIR / filename)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )
    return df

####################################### LOADER FUNCITONS ######################################
def load_wards(engine):
    print("Loading wards...")
    wards = pd.DataFrame ({
        'ward_number': range(1, 15),
        'ward_name': [f'Ward {i}' for i in rage(1, 15)]
    })
    wards.to_sql('ward', engine, if_exists='append', index=False)
    print("Loaded wards.")

def load_ward_population(engine):
    print("Loading population data...")
    df = load_csv("_Ward_population.csv")
    pop_df = pd.DataFrame ({
        'ward_number': df['ward'],
        'total': df['population'],
        'density': None,
        'total_households': None
    })
    pop_df.to_sql('ward_population', engine, if_exists='append', index=False)
    print('Loaded ward population.')

def load_ward_crime(engine):
    print("Loading ward crime...")
    df = load_csv("_Ward_Crime.csv")
    crime_df = pd.DataFrame({
        'ward_number': df['ward'],
        'total': df['total_crime'],
        'rate_per_1000': df['rate_per_1000_residents']
    })
    crime_df.to_sql('ward_crime', engine, if_exists='append', index=False)
    print("Loaded ward crime.")

def load_ward_disorder(engine):
    print("Loading ward disorder...")
    df = load_csv("_Ward_Disorder.csv")
    disorder_df = pd.DataFrame({
        'ward_number': ['ward'],
        'total': df['total_disorder'],
        'rate_per_1000': df['rate_per_1000_residents']
    })
    disorder_df.to_sql('ward_disorder', engine, if_exists='append', index=False)
    print("Loaded ward disorder.")

def load_ward_age_gender(engine):
    print("Loading age and gender...")
    df = load_csv("_Ward_Age_Sex.csv")
    a_g_df = pd.DataFrame ({
        'ward_number': df['ward'],
        'age_group': df['agegroup'],
        'male_count': df['men'],
        'female_count': df['women'],
        'total': df['total']
    })
    a_g_df.to_sql('ward_age_gender', engine, if_exists='append', index=False)
    print("Loaded ward age and gender.")

def load_ward_education(engine):
    print("Loading ward education...")
    df = load_csv("_Ward_Education.csv")
    df = df[df['category'].notna() & (df['category'] != 'Total')]
    education_df = pd.DataFrame ({
        'ward_number': df['ward'],
        'education_level': df['category'],
        'count': df['number'],
        'percent': df['percent']
    })
    education_df.to_sql('ward_education', engine, if_exists='append', index=False)
    print("Loaded ward education.")

def load_ward_income(engine):
    