## Loads data from the csv's into PostgreSQL database using the provided schema

import pandas as pd
import os
from sqlalchemy import create_engine
from pathlib import Path
import sys
import time

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
    print("Loading ward income...")
    df = load_csv("_Ward_household_Income.csv")
    income_column = [col for col in df.columns if col not in ['ward', 'total']]
    records = []
    for _, row in df.iterrows():
        ward_num = int(row['ward'].replace('WARD ', ''))
        for income_group in income_column:
            records.append({
                'ward_number': ward_num,
                'income_group': income_group,
                'household_count': row[income_group]
            })
    income_df = pd.DataFrame(records)
    income_df.to_sql('ward_income', engine, if_exists='append', index=False)
    print("Loaded ward income.")

def load_labour_force(engine):
    print("Loading ward labour force...")
    df = load_csv("_Ward_Labour_Force.csv")
    labour_df = pd.DataFrame ({
        'ward_number': df['ward'],
        'gender': df['gender'],
        'eligible': df['population_15plus'],
        'in_labour_force': df['in_labour_force'],
        'employed': df['employed'],
        'self_employed': df['self_employed'],
        'unemployed': df['unemployed'],
        'not_in_labour_force': df['not_in_labour_force'],
        'participation_rate': df['labour_force_participation_rate'],
        'employment_rate': df['employment_rate'],
        'unemployment_rate': df['unemployment_rate']
    })
    labour_df.to_sql('ward_labour_force', engine, if_exists='append', index=False)
    print("Loaded labour force.")

def load_ward_transport_mode(engine):
    print("Loading ward transportation mode...")
    df = load_csv("_Ward_Work_Transport.csv")
    transport_df = pd.DataFrame ({
        'ward_number': df['ward'],
        'transport_mode': df['mode'],
        'count': df['number'],
        'percent': df['percent']
    })
    transport_df.to_sql('ward_transport_mode', engine, if_exists='append', index=False)
    print("Loaded ward transportation modes.")

def load_ward_transit_stops(engine):
    print("Loading transport stops...")
    df = load_csv("_Ward_Transit_Stops.csv")
    transit_df = pd.DataFrame ({
        'ward_number': df['ward_num'],
        'total': df['total_stops'],
        'active': df['active_stops'],
        'inactive': df['inactive_stops']
    })
    transit_df.to_sql('ward_transit_stops', engine, if_exists='append', index=False)
    print("Loaded transportation stops")

def load_ward_recreation(engine):
    print("Loading ward recreation facilities...")
    df = load_csv("_Ward_Rec_Facilities.csv")
    facility_cols = [col for col in df.columns if col not in ['ward', 'total']]
    records = []
    for _, row in df.iterrows():
        for facilitiy_type in facility_cols:
            if row[facilitiy_type] > 0:
                records.append({
                    'ward_number' : row['ward'],
                    'facility_type': facilitiy_type,
                    'count': row[facilitiy_type]
                })
    rec_df = pd.DataFrame(records)
    rec_df.to_sql('ward_recreation', engine, if_exists='append', index=False)
    print("Loaded ward recreatio nfacilities.")

def load_community_services(engine):
    print("Loading community services...")
    df = load_csv("_Ward_Community_Services.csv")
    service_cols = [col for col in df.columns if col not in ['ward', 'total']]
    records= []
    for _, row in df.iterrows():
        for service_type in service_cols:
            if row[service_type] > 0:
                records.append({
                    'ward_number': row['ward'],
                    'service_type': service_type,
                    'count': row[service_type]
                })
    services_df = pd.DataFrame(records)
    services_df.to_sql('ward_services', engine, if_exists='append', index=False)
    print("Loaded community services.")

def load_election_data(engine):
    print('Loading election data...')
    df = load_csv("_Ward_Election_Results.csv")

    election_data = {
        'election_id': [1],
        'year': [2021],
        'election_type': ['Municipal'],
        'election_date': ['2021-10-18']
    }
    election_df = pd.DataFrame(election_data)
    election_df.to_sql('election', engine, if_exists='append', index=False)

    races= []
    race_id = 1
    if 'MAYOR' in df['officetype'].values:
        races.append({
            'race_id': race_id,
            'election_id': 1,
            'type': 'MAYOR',
            'ward_number': None
        })
        race_id += 1
    
    for ward_num in sorted(df['ward'].unique()):
        races.append({
            'race_id': race_id,
            'election_id': 1, 
            'type': 'COUNCILLOR',
            'ward_number': ward_num
        })
        race_id += 1
    
    race_df = pd.DataFrame(races)
    race_df.to_sql('race', engine, if_exists='append', index=False)

    candidates = df[['candidatename']].drop_duplicates().reset_index(drop=True)
    candidates['candidate_id'] = range(1, len(candidates) + 1)
    candidates.columns = ['name', 'candidate_id']
    candidates = candidates[['candidate_id', 'name']]
    candidates.to_sql('candidate', engine, if_exists='append', index=False)

    candidate_id_map = dict(zip(candidates['name'], candidates['candidate_id']))
    candidacies=[]
    for _, row in df.interrows():
        candidate_id = candidate_id_map[row['candidatename']]
        if row['officetype'] == 'MAYOR':
            race_id = race_df[race_df['type'] == 'MAYOR']['race_id'].values[0]
        else:
            race_id = race_df [
                (race_df['type'] == 'COUNCILLOR') & (race_df['ward_number'] == row['ward'])
            ]['race_id'].values[0]
        candidacies.append({
            'candidate_id': candidate_id,
            'race_id': race_id
        })
    candidacy_df = pd.DataFrame(candidacies).drop_duplicates()
    candidacy_df.to_sql('candidacy', engine, if_exists='append', index=False)

    stations = df [['votingstationcode', 'ward', 'votingstation', 'votingstationtype']].drop_duplicates()
    stations.columns = ['station_code', 'ward_number', 'station_name', 'stationg_type']
    stations.to_sql('voting_station', engine, if_exists='append', index=False)

    results=[]
    for _, row in df.interrows():
        candidate_id = candidate_id_map[row['candidatename']]
        if row['officetype'] == "MAYOR":
            race_id = race_df[race_df['type'] == 'MAYOR']['race_id'].values[0]
        else:
            race_id = race_df [
                (race_df['type'] == 'COUNCILLOR') & (race_df['ward_number'] == row['ward'])
            ]['race_id'].values[0]
        results.append({
            'station_code': row['votingstationcode'],
            'candidate_id': candidate_id,
            'race_id': race_id,
            'votes': row['votes']
        })
    results_df = pd.DataFrame(results)
    results_df.to_sql('election_result', engine, if_exists='append', index=False)

################################## MAIN SCRIPT ##########################################

def run_script():
    print("CALGARY WARD DATA INITIALIZING")
    try:
        engine = get_engine()
    except Exception as e:
        print("Failed to connect to DB: {e}")
        sys.exit(1)

    try:
        load_wards(engine)
        load_ward_population(engine)
        load_ward_crime(engine)
        load_ward_disorder(engine)
        load_ward_age_gender(engine)
        load_ward_education(engine)
        load_ward_income(engine)
        load_labour_force(engine)
        load_ward_transport_mode(engine)
        load_ward_transit_stops(engine)
        load_ward_recreation(engine)
        load_community_services(engine)
        load_election_data(engine)
        print("Success.")
    except Exception as e:
        print("Failed to load data: {e}.")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_script()