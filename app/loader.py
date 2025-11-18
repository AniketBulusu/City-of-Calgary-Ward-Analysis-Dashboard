## Loads data from the csv's into PostgreSQL database using the provided schema

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from pathlib import Path
import sys

DB_CONFIG = {
    'host': 'localhost',
    'database': 'calgary_wards',
    'user': 
}