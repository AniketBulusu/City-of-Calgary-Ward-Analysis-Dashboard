import os
import psycopg2
import pandas as pd
from psycopg2 import sql
import chardet
import matplotlib.pyplot as plt # type: ignore



# PostgreSQL config
conn = psycopg2.connect(
    dbname="cpsc471",
    user="postgres",
    password="GurgaonB78",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# CSV folder path
csv_folder = "C:\\Users\\Anike\\Downloads\\CPSC471FINALPROJECT\\cpsc471p\\datasets"


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
                f"[⚠] Failed with {encoding} due to {type(e).__name__}, retrying with latin1 and skipping bad lines...")
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

        print(f"[✔] Imported {file} into table {table_name}")





# Visualizing Population by Ward using Matplotlib
cursor.execute('SELECT "Ward ", "Population" FROM "_ward_crime";')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df = pd.DataFrame(rows, columns=columns)

# ✅ Clean and convert population to integers as l think Population was stored as a string originally
df["Population"] = df["Population"].str.replace(",", "").astype(int)

# Sam and Sultan, so l found that our column name "Ward " has a trailing space which might cause issues later on. So yeah, just keep that in consideration. 
df.rename(columns={"Ward ": "Ward"}, inplace=True)

#  Plotting the data. Just used to w3schools as reference. I honestly think that is the way to go for out visualizations. However, l think we can explore more options later on in terms of more eye catching visualizations. 
plt.figure(figsize=(10, 6))
plt.bar(df["Ward"], df["Population"], color="mediumseagreen", edgecolor="black")
plt.title("Population by Ward")
plt.xlabel("Ward")
plt.ylabel("Population")
plt.xticks(df["Ward"])
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()
            
cursor.close()
conn.close()


# TO-DO : Create Data Visualizations using Matplotlib,Seaborn, and Plotly to get an insight on how we can visualize the data.
