import os
import psycopg2
import pandas as pd
from psycopg2 import sql
import chardet
import matplotlib.pyplot as plt # type: ignore
import numpy as np




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



# --- Fetch data for visualizations ---

# ***1️*** Population by Ward
cursor.execute('SELECT "Ward ", "Population" FROM "_ward_crime";')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df_pop = pd.DataFrame(rows, columns=columns)
df_pop["Population"] = df_pop["Population"].str.replace(",", "").astype(int)
df_pop.rename(columns={"Ward ": "Ward"}, inplace=True)

# ***2️*** Crime Rate by Ward
cursor.execute('SELECT "Ward ", "Rate Per 1000 Residents" FROM "_ward_crime";')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df_crime = pd.DataFrame(rows, columns=columns)
df_crime["Rate Per 1000 Residents"] = df_crime["Rate Per 1000 Residents"].astype(float)
df_crime.rename(columns={"Ward ": "Ward"}, inplace=True)

# ***3️*** Age Group Distribution by Ward
# Fetch and load data
cursor.execute('SELECT "Ward", "AgeGroup", "Men", "Women" FROM "_ward_age_sex";')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df_age = pd.DataFrame(rows, columns=columns)

# Keep only total rows per ward
df_age_total = df_age[df_age["AgeGroup"] == "Total"].copy()

# Convert numeric columns
df_age_total["Men"] = df_age_total["Men"].astype(int)
df_age_total["Women"] = df_age_total["Women"].astype(int)

# ***4*** Total # of Voters by AgeGroup sumed by wards

cursor.execute('''
    SELECT "Ward", "AgeGroup", "Total"
    FROM "_ward_age_sex"
    WHERE "AgeGroup" IN (
        '15-19', '20-24', '25-29', '30-34', '35-39', '40-44',
        '45-49', '50-54', '55-59', '60-64'
    )
    ORDER BY "AgeGroup", "Ward";
''')

rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df_voters = pd.DataFrame(rows, columns=columns)

df_voters["Total"] = df_voters["Total"].astype(int)

df_agegroup_sum = (
    df_voters.groupby("AgeGroup")["Total"]
    .sum()
    .reset_index()
)







# --- Create 2x2 dashboard ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))



# Chart 1: Population by Ward
axes[0, 0].bar(
    df_pop["Ward"].astype(str),   # convert to string so all wards show up
    df_pop["Population"],
    color="mediumseagreen",
    edgecolor="black"
)
axes[0, 0].set_title("Population by Ward", pad=15)
axes[0, 0].set_xlabel("Ward")
axes[0, 0].set_ylabel("Population")
axes[0, 0].grid(axis="y", linestyle="--", alpha=0.7)
# Chart 2: Crime Rate by Ward (properly descending)
df_crime_sorted = df_crime.sort_values("Rate Per 1000 Residents", ascending=False)

axes[0, 1].bar(
    df_crime_sorted["Ward"].astype(str),   # keep ward labels in sorted order
    df_crime_sorted["Rate Per 1000 Residents"],
    color="Blue",
    edgecolor="black"
)
axes[0, 1].set_title("Crime Rate Per 1000 Residents by Ward", pad=15)
axes[0, 1].set_xlabel("Ward")
axes[0, 1].set_ylabel("Rate Per 1000 Residents")
axes[0, 1].grid(axis="y", linestyle="--", alpha=0.7)


# -Chart 3: Men vs Women by Ward ---
x = np.arange(len(df_age_total["Ward"]))
width = 0.35

axes[1, 0].bar(x - width/2, df_age_total["Men"], width, label="Men", color="royalblue", edgecolor="black")
axes[1, 0].bar(x + width/2, df_age_total["Women"], width, label="Women", color="lightcoral", edgecolor="black")

axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(df_age_total["Ward"])
axes[1, 0].set_title("Distribution of Men vs Women by Ward", pad=15)
axes[1, 0].set_xlabel("Ward")
axes[1, 0].set_ylabel("Population")
axes[1, 0].legend()
axes[1, 0].grid(axis="y", linestyle="--", alpha=0.7)
axes[1, 0].legend(fontsize=7)


# Chart 4: Age Group Voted Population by Ward
axes[1, 1].scatter(
    df_agegroup_sum["AgeGroup"],    # X-axis: age groups
    df_agegroup_sum["Total"],       # Y-axis: summed voters
    color="Orange",
    edgecolor="black"
)

axes[1, 1].set_title("Total Voters by Age Group summed across Wards", pad=15)
axes[1, 1].set_xlabel("Age Group")
axes[1, 1].set_ylabel("Total Voters")

axes[1, 1].grid(axis="y", linestyle="--", alpha=0.7)

# Titles
fig.suptitle(
    "Calgary Ward Voting Analysis Dashboard",
    fontsize=18,
    fontweight="bold",
    x=0.5,
    y=0.99
)
fig.text(
    0.5, 0.91,
    "Is Crime Rate influenced by Population?",
    ha="center",
    fontsize=13,
    fontweight="bold",
    style="italic",
    color="gray"
)

fig.text(
    0.5, 0.435,
    "What type of voter turnout is expected across genders and age groups?",
    ha="center",
    fontsize=13,
    fontweight="bold",
    color="gray",
    style="italic",
)

# Layout tweaks
plt.tight_layout(rect=[0, 0, 1, 0.91])
plt.subplots_adjust(hspace=0.6, wspace=0.3)
plt.show()



  
cursor.close()
conn.close()


