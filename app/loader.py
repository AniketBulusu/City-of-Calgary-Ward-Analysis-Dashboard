## Loads data from the csv's into PostgreSQL database using the provided schema

import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine
from pathlib import Path
import sys

DATABSE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABSE_URL)

DATA_DIR = Path("/app/datasets")

def load_ward_population():
    df = pd.read_csv(DATA_DIR / "_wa")

DB_CONFIG = {
    'host': 'localhost',
    'database': 'calgary_wards',
    'user': 
}