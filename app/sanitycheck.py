# Was experiencing lots of issues trying to figure out why data wasn't being loaded into app.
# Finally diagnosed as the app loading much faster than database is populated.
# This is a debugging tool written just to make sure the database is ready.
# All it does is run random checks to make sure data exists in tables.
# checks table names, counts, rows, queries, and returns the sumary at the end.

import os
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://appuser:app_password@db:5432/calgary_ward_db"
)

EXPECTED_TABLES = [
    "ward",
    "election",
    "race",
    "candidate",
    "candidacy",
    "voting_station",
    "election_result",
    "ward_population",
    "ward_income",
    "ward_education",
    "ward_age_gender",
    "ward_labour_force",
    "ward_transport_mode",
    "ward_crime",
    "ward_disorder",
    "ward_transit_stops",
    "ward_recreation",
    "community_services",
]


def check_table_exists(conn, table_name):
    query = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
              AND table_name = :tbl
        );
    """)
    return conn.execute(query, {"tbl": table_name}).scalar()


def count_rows(conn, table_name):
    return conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()


def sample_rows(conn, table_name, limit=5):
    try:
        df = pd.read_sql(text(f"SELECT * FROM {table_name} LIMIT {limit}"), conn)
        return df
    except Exception:
        return None


def main():
    engine = create_engine(DATABASE_URL)

    # Use ONE connection for all checks
    with engine.connect() as conn:
        print("\n=== Checking expected tables exist ===")

        for tbl in EXPECTED_TABLES:
            exists = check_table_exists(conn, tbl)
            print(f"[{'OK' if exists else 'ERR'}] Table exists: {tbl}")

        print("\n=== Row counts for tables ===")
        row_issues = []
        for tbl in EXPECTED_TABLES:
            try:
                rows = count_rows(conn, tbl)
                print(f"{tbl}: {rows}")

                if rows > 0:
                    sample = sample_rows(conn, tbl)
                    if sample is not None:
                        print(f"{tbl}:\n{sample}")
                else:
                    print(f"{tbl}: (no rows)")
                    row_issues.append(f"Table '{tbl}' has 0 rows")
            except Exception as e:
                print(f"Could not read table {tbl}: {e}")
                row_issues.append(f"Table '{tbl}' missing")

        print("\n=== Others ===")

        # Ward numbers 1–14 present?
        try:
            ward_df = pd.read_sql(text("SELECT ward_number FROM ward ORDER BY ward_number"), conn)
            ward_nums = ward_df["ward_number"].tolist()
            missing = [w for w in range(1, 15) if w not in ward_nums]
            if missing:
                print(f"Missing ward numbers: {missing}")
            else:
                print("All wards 1–14 present")
        except Exception as e:
            print(f"Could not check ward numbers: {e}")

        # Turnout per ward
        turnout_query = text("""
            SELECT
                vs.ward_number,
                SUM(er.votes) AS total_votes
            FROM election_result er
            JOIN voting_station vs
              ON er.station_code = vs.station_code
            GROUP BY vs.ward_number
            ORDER BY vs.ward_number;
        """)

        try:
            turnout = pd.read_sql(turnout_query, conn)
            if turnout.empty:
                print("Turnout query returned no rows")
            else:
                print("Turnout sample:\n", turnout.head())
        except Exception as e:
            print(f"Turnout query failed: {e}")

        if not row_issues:
            print("All checks passed.")
        else:
            print("Sanity check detected issues:")
            for issue in row_issues:
                print("  - " + issue)


if __name__ == "__main__":
    main()
