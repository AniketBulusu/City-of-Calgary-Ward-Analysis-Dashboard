import os
import psycopg2
import pandas as pd
from psycopg2 import sql
import chardet


# PostgreSQL config
conn = psycopg2.connect(
    dbname="cpsc471-final",
    user="sultanalzoghaibi",
    password="",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# CSV folder path
csv_folder = "/Users/sultanalzoghaibi/PycharmProjects/cpsc471p/datasets"


# Map pandas dtypes to PostgreSQL
def infer_pg_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    else:
        return "TEXT"


# Loop through all CSV files
for file in os.listdir(csv_folder):
    if file.endswith(".csv"):
        table_name = os.path.splitext(file)[0].lower()
        file_path = os.path.join(csv_folder, file)

        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding = result['encoding'] if result['encoding'] else 'latin1'

        try:
            df = pd.read_csv(file_path, encoding=encoding, on_bad_lines="skip")
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            print(
                f"[WARNING] Failed with {encoding} due to {type(e).__name__}, retrying with latin1 and skipping bad lines...")
            df = pd.read_csv(file_path, encoding=encoding, on_bad_lines="skip")
        # Ensure all column names are strings
        df.columns = df.columns.map(str)


        # Build CREATE TABLE SQL
        columns = []
        for col in df.columns:
            pg_type = infer_pg_type(df[col].dtype)
            columns.append(f'"{col}" {pg_type}')

        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(columns)});'

        # Execute create
        cursor.execute(create_table_sql)
        conn.commit()

        # Insert data row-by-row
        for i, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            insert_sql = sql.SQL(f'INSERT INTO "{table_name}" VALUES ({placeholders});')
            cursor.execute(insert_sql, list(row))
        conn.commit()

        print(f"[SUCCESS] Imported {file} into table {table_name}")

cursor.close()
conn.close()