#!/bin/bash
set -e

## Used to make sure the app doesn't load before the database is ready

echo ""
echo "STARTUP SCRIPT"
echo ""

# Wait for database to be ready - it runs a query to see if we have data
echo "Waiting for database to be ready..."
python3 << PYTHON
import time
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

max_retries = 30
for i in range(max_retries):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready!")
        break
    except Exception as e:
        if i < max_retries - 1:
            print(f"   Waiting... (attempt {i+1}/{max_retries})")
            time.sleep(2)
        else:
            print(f"Database connection failed: {e}")
            exit(1)
PYTHON

# Check if data is already loaded - if the data is returned we are good
echo ""
echo "Checking if data is already loaded..."
WARD_COUNT=$(python3 << PYTHON
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM ward"))
        count = result.fetchone()[0]
        print(count)
except:
    print(0)
PYTHON
)

## in this case, we have to run the loader

if [ "$WARD_COUNT" -eq 0 ]; then
    echo "No data found. Loading data..."
    python app/loader.py
    
    if [ $? -eq 0 ]; then
        echo "Data loaded successfully!"
    else
        echo "Data loading failed!"
        exit 1
    fi
else
    echo "Data already loaded ($WARD_COUNT wards found). Skipping load."
fi

echo ""
echo "Starting app..."
echo ""

# Start the application
exec python app/app.py