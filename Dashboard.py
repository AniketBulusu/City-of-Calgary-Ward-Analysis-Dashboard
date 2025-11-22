import os
import psycopg2
import pandas as pd
from psycopg2 import sql
import chardet
import matplotlib.pyplot as plt # type: ignore
import numpy as np
import seaborn as sns




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


# ------------------- POPULATION CHARACTERISTICS VISUALIZATIONS -------------------

#1: HOW MANY PEOPLE IN EACH WARD HAVE VOTED OUT OF THE WARD’S RESPECTIVE POPULATION
cursor.execute('''
    SELECT
        p."ward",
        p."population",
        SUM(REPLACE(r."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_population" p
    LEFT JOIN "_ward_election_results" r
        ON p."ward" = r."Ward"
    GROUP BY p."ward", p."population"
    ORDER BY p."ward";
''')


results = cursor.fetchall()
wards = [row[0] for row in results]
populations = [row[1] for row in results]
total_votes = [row[2] for row in results]
x = np.arange(len(wards))
width = 0.35
fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, populations, width, label='Population', color='skyblue')
bars2 = ax.bar(x + width/2, total_votes, width, label='Total Votes', color='salmon')
ax.set_xlabel('Ward')
ax.set_ylabel('Number of People')
ax.set_title('Is Ward Population Proportional to Voter Turnout?')
ax.set_xticks(x)
ax.set_xticklabels(wards)
ax.legend()
plt.show()


# 2: HOW MANY VOTES DOES DID VARIOUS MAYOR CANDIDATES RECEIVE IN TOTAL, COMPARED TO THE NUMBER OF VOTES THEY RECEIVED IN EACH WARD
cursor.execute('''SELECT
    r."Ward",
    r."CandidateName",
    SUM(REPLACE(r."Votes", ',', '')::INT) AS TotalVotes,
    p."population"
FROM "_ward_election_results" r
JOIN "_ward_population" p
    ON r."Ward" = p."ward"
WHERE r."OfficeType" = 'MAYOR'
GROUP BY r."Ward", r."CandidateName", p."population"
ORDER BY r."Ward", TotalVotes DESC;
''')

results = cursor.fetchall()
wards = list(set(row[0] for row in results))
candidates = list(set(row[1] for row in results))
ward_indices = {ward: i for i, ward in enumerate(wards)} 
candidate_votes = {candidate: [0] * len(wards) for candidate in candidates}
for row in results:
    ward = row[0]
    candidate = row[1]
    votes = row[2]
    idx = ward_indices[ward]
    candidate_votes[candidate][idx] = votes
x = np.arange(len(wards))
fig, ax = plt.subplots(figsize=(14, 7))
fig.set_size_inches(30, 10)
bottom = np.zeros(len(wards))
for candidate, votes in candidate_votes.items():
    bars = ax.bar(x, votes, bottom=bottom, label=candidate)
    bottom += np.array(votes)
ax.set_xlabel('Ward')
ax.set_ylabel('Number of Votes')
ax.set_title('What is the turnout for each Mayor Candidate by Voted Population of each Ward')
ax.set_xticks(x)
ax.set_xticklabels(wards)
ax.legend(
    bbox_to_anchor=(1, 1),
    loc='upper left',
    fontsize='6'  
)
plt.show()

  



# -------------------------------- WARD_LABOUR_FORCE CHARACTERISTICS  ---------------------------

# 3. DO MORE ECONOMICALLY ACTIVE WARDS VOTE MORE?

cursor.execute('''
    SELECT
        lf."Ward",
        lf."In_Labour_Force" AS EconomicActivePopulation,
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_labour_force" lf
    LEFT JOIN "_ward_election_results" er
        ON lf."Ward" = er."Ward"
    GROUP BY lf."Ward", lf."In_Labour_Force"
    ORDER BY lf."Ward";
''')


results = cursor.fetchall()
economic_active_populations = [row[1] for row in results]
total_votes = [row[2] for row in results]
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(economic_active_populations, total_votes, s=np.array(economic_active_populations)/10, alpha=0.5, color='blue')
ax.set_xlabel('Economically Active Population')
ax.set_ylabel('Total Votes')
ax.set_title('Do more Economically Active Wards vote more?')
plt.show()


# 4. WHICH MAYOR CANDIDATES APPEALED TO THE LEAST AND MOST ECONOMICALLY ACTIVE WARDS?
cursor.execute('''
    SELECT
        er."CandidateName",
        lf."In_Labour_Force" AS EconomicActivePopulation,
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_labour_force" lf
        ON er."Ward" = lf."Ward"
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", lf."In_Labour_Force"
    ORDER BY er."CandidateName", TotalVotes DESC;
''')

results = cursor.fetchall()

candidates = list(set(row[0] for row in results))
candidate_votes = {candidate: [] for candidate in candidates}

for row in results:
    candidate = row[0]
    economic_active_population = row[1]
    votes = row[2]
    candidate_votes[candidate].append((economic_active_population, votes))

fig, ax = plt.subplots(figsize=(14, 7))

for candidate, data in candidate_votes.items():
    economic_active_populations = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(economic_active_populations, votes, label=candidate, alpha=0.7)

ax.set_xlabel('Economically Active Population (In Labour Force)')
ax.set_ylabel('Total Votes')
ax.set_title('Do Mayor Candidates Perform Better in Economically Active Wards?')
ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

plt.tight_layout()
plt.show()







# --------------------------------------- WARD COMMUNITY SERVICES CHARACTERISTICS -----------------------------------

# 5. WHAT TYPE OF COMMUNITY SERVICES DRIVE VOTER TURNOUT IN WARDS?
cursor.execute('''
    SELECT
        cs."Ward",
        cs."Total",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_community_services" cs
    LEFT JOIN "_ward_election_results" er
        ON cs."Ward" = er."Ward"
    GROUP BY cs."Ward", cs."Total"
    ORDER BY cs."Ward";
''')
results = cursor.fetchall()
wards = [row[0] for row in results]
community_services = [row[1] for row in results]
total_votes = [row[2] for row in results]
fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(community_services, total_votes, s=np.array(community_services)*10, alpha=0.5, color='green')
ax.set_xlabel('Number of Community Services')
ax.set_ylabel('Total Votes')
ax.set_title('Does the Number of Community Services in a Ward Influence Voter Turnout?')
plt.show()



# 6. DO WARDS WITH COMMUNITY CENTRES MEAN MORE VOTER TURNOUT FOR CERTAIN MAYOR CANDIDATES?

cursor.execute('''
    SELECT
        er."CandidateName",
        cs."Community Centre",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_community_services" cs
        ON er."Ward" = cs."Ward"
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", cs."Community Centre"
    ORDER BY er."CandidateName", TotalVotes DESC;
''')


results = cursor.fetchall()
candidates = list(set(row[0] for row in results))
candidate_votes = {candidate: [] for candidate in candidates}
for row in results:
    candidate = row[0]
    community_centres = row[1]
    votes = row[2]
    candidate_votes[candidate].append((community_centres, votes))
fig, ax = plt.subplots(figsize=(14, 7))
for candidate, data in candidate_votes.items():
    community_centres = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(community_centres, votes, label=candidate, alpha=0.7)
ax.set_xlabel('Number of Community Centres')
ax.set_ylabel('Total Votes')
ax.set_title('Do Wards with Community Centres Mean More Voter Turnout for Certain Mayor Candidates?')
ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.show()



# --------------------------------------- _WARD_CRIME CHARACTERISTICS -----------------------------------


# 7. DOES A HIGHER CRIME RATE IN A WARD CORRELATE WITH LOWER VOTER TURNOUT?

cursor.execute('''
    SELECT
        c."Ward " AS Ward,
        c."Total Crime",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_crime" c
    LEFT JOIN "_ward_election_results" er
        ON c."Ward " = er."Ward"
    GROUP BY c."Ward ", c."Total Crime"
    ORDER BY c."Ward ";
''')

results = cursor.fetchall()
wards = [row[0] for row in results]
total_crimes = np.array([row[1] for row in results])
total_votes = np.array([row[2] for row in results])

fig, ax = plt.subplots(figsize=(10, 6))


ax.scatter(total_crimes, total_votes, s=30, alpha=0.5, color='red')
m, b = np.polyfit(total_crimes, total_votes, 1)
ax.plot(total_crimes, m*total_crimes + b, linestyle='--')

ax.set_xlabel('Total Crimes in Ward')
ax.set_ylabel('Total Votes')
ax.set_title('Does a Higher Crime Rate in a Ward Correlate with Lower Voter Turnout?')
plt.show()



# 8. WHICH MAYOR CANDIDATES PERFORM BETTER IN WARDS WITH HIGHER CRIME RATES?

cursor.execute('''
    SELECT
        er."CandidateName",
        c."Total Crime",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_crime" c
        ON er."Ward" = c."Ward "
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", c."Total Crime"
    ORDER BY er."CandidateName", TotalVotes DESC;
''')


results = cursor.fetchall()
candidates = list(set(row[0] for row in results))
candidate_votes = {candidate: [] for candidate in candidates}
for row in results:
    candidate = row[0]
    total_crime = row[1]
    votes = row[2]
    candidate_votes[candidate].append((total_crime, votes))
fig, ax = plt.subplots(figsize=(14, 7))
for candidate, data in candidate_votes.items():
    total_crimes = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(total_crimes, votes, label=candidate, alpha=0.7)
ax.set_xlabel('Total Crimes in Ward')
ax.set_ylabel('Total Votes')
ax.set_title('Which Mayor Candidates Perform Better in Wards with Higher Crime Rates?')
ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.show()



# ------------------------------------------ _WARD_DISORDERS CHARACTERISTICS -----------------------------------

# 9. DOES TOTAL DISORDER IN A WARD AFFECT VOTER TURNOUT?
cursor.execute('''
    SELECT
        d."Ward ", 
        d."Total Disorder",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_disorder" d
    LEFT JOIN "_ward_election_results" er
        ON d."Ward " = er."Ward"
    GROUP BY d."Ward ", d."Total Disorder"
    ORDER BY d."Ward ";
''')

results = cursor.fetchall()
wards = [row[0] for row in results]
total_disorder = np.array([row[1] for row in results])
total_votes = np.array([row[2] for row in results])

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(total_disorder, total_votes, s=50, alpha=0.6)

# Trendline
m, b = np.polyfit(total_disorder, total_votes, 1)
ax.plot(total_disorder, m * total_disorder + b, linestyle='--')

ax.set_xlabel('Total Disorder Incidents in Ward')
ax.set_ylabel('Total Votes')
ax.set_title('Do Wards with Higher Disorder result in Higher Rates of Voter Turnout?')

plt.tight_layout()
plt.show()


# 10. WHICH MAYOR CANDIDATES PERFORM BETTER IN WARDS WITH HIGHER DISORDER RATES?

cursor.execute('''
    SELECT
        er."CandidateName",
        d."Total Disorder",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_disorder" d
        ON er."Ward" = d."Ward "
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", d."Total Disorder"
    ORDER BY d."Total Disorder" DESC, TotalVotes DESC;
''')

results = cursor.fetchall()

candidates = list(set(row[0] for row in results))
candidate_data = {candidate: [] for candidate in candidates}

for row in results:
    candidate, disorder, votes = row
    candidate_data[candidate].append((disorder, votes))

fig, ax = plt.subplots(figsize=(14,7))
for candidate, data in candidate_data.items():
    disorder = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(disorder, votes, alpha=0.7, label=candidate)

ax.set_xlabel("Ward Disorder Score")
ax.set_ylabel("Votes Received")
ax.set_title("Do Mayor Candidates Perform Better in High-Disorder Wards?")
ax.legend(bbox_to_anchor=(1,1))
plt.tight_layout()
plt.show() 




# ------------------------------------ WARD_EDUCATION CHARACTERISTICS ---------------------------------------   


# 11. DO WARDS THAT HAVE POST-SECONDARY EDUCATION RESUL IN HIGHER VOTER TURNOUT?

cursor.execute("""
    SELECT
        ed."Ward",
        MAX(ed."Number") FILTER (WHERE ed."Category" = 'Post Secondary') AS "Post-Secondary",
        (SELECT SUM(REPLACE("Votes", ',', '')::INT) 
         FROM "_ward_election_results" er
         WHERE er."Ward" = ed."Ward") AS "Total Votes"
    FROM "_ward_education" ed
    GROUP BY ed."Ward"
    ORDER BY ed."Ward";

""")

results = cursor.fetchall()

# Unpack the results
wards = [row[0] for row in results]
post_secondary = [row[1] for row in results]
total_votes = [row[2] for row in results]


# Plot
x = np.arange(len(wards))
width = 0.35

fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(x - width/2, post_secondary, width, label='Post-Secondary Population', color='orange')
ax.bar(x + width/2, total_votes, width, label='Total Votes', color='purple')

ax.set_xlabel('Ward')
ax.set_ylabel('Number of People')
ax.set_title('Do Wards with More Post-Secondary Education Have Higher Voter Turnout?')
ax.set_xticks(x)
ax.set_xticklabels(wards)

ax.legend()
plt.tight_layout()
plt.show()



# 12. DO WARDS WITH POST SECONDARY EDUCATION MEAN MORE VOTER TURNOUT FOR CERTAIN MAYOR CANDIDATES?
cursor.execute("""
    SELECT
        er."CandidateName",
        MAX(ed."Number") FILTER (WHERE ed."Category" = 'Post Secondary') AS post_secondary,
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_education" ed
        ON er."Ward" = ed."Ward"
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", ed."Number"
    ORDER BY post_secondary, TotalVotes DESC;
""")

results = cursor.fetchall()

candidates = list(set(row[0] for row in results))
candidate_data = {candidate: [] for candidate in candidates}

for row in results:
    candidate, post_secondary, votes = row
    candidate_data[candidate].append((post_secondary, votes))

fig, ax = plt.subplots(figsize=(14, 7))
for candidate, data in candidate_data.items():
    post_secondary = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(post_secondary, votes, alpha=0.7, label=candidate)

ax.set_xlabel("Post-Secondary Education Population")
ax.set_ylabel("Votes Received")
ax.set_title("Do Mayor Candidates Perform Better in Wards with Higher Post-Secondary Education?")
ax.legend(bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()



# -------------------------------- _WARD_HOUSEHOLD_INCOME CHARACTERISTICS -----------------------------------

# 13. DOES A HIGHER AVERAGE HOUSEHOLD INCOME IN A WARD RESULT WITH HIGHER VOTER TURNOUT?
cursor.execute("""
    SELECT
        CAST(REPLACE(hi."Ward", 'WARD ', '') AS INT) AS Ward,
        hi."Under_$20000" + hi."$20000_to_$39999" + hi."$40000_to_$59999" + 
        hi."$60000_to_$79999" + hi."$80000_to_$99999" + hi."$100000_to_$124999" +
        hi."$125000_to_$149999" + hi."$150000_to_$199999" + hi."$200000_and_over" AS TotalHouseholds,
        hi."Under_$20000",
        hi."$20000_to_$39999",
        hi."$40000_to_$59999",
        hi."$60000_to_$79999",
        hi."$80000_to_$99999",
        hi."$100000_to_$124999",
        hi."$125000_to_$149999",
        hi."$150000_to_$199999",
        hi."$200000_and_over",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_household_income" hi
    LEFT JOIN "_ward_election_results" er
        ON CAST(REPLACE(hi."Ward", 'WARD ', '') AS INT) = er."Ward"::INT
    GROUP BY hi."Ward", hi."Under_$20000", hi."$20000_to_$39999", hi."$40000_to_$59999",
             hi."$60000_to_$79999", hi."$80000_to_$99999", hi."$100000_to_$124999",
             hi."$125000_to_$149999", hi."$150000_to_$199999", hi."$200000_and_over"
    ORDER BY CAST(REPLACE(hi."Ward", 'WARD ', '') AS INT);
""")

results = cursor.fetchall()

data = []
for row in results:
    ward = row[0]
    total_households = row[1]
    votes = row[11]
    
    # Calculate average income using midpoint of each bracket
    weighted_income = (
        row[2] * 10000 +      # under 20k
        row[3] * 30000 +      # 20-40k
        row[4] * 50000 +      # 40-60k
        row[5] * 70000 +      # 60-80k
        row[6] * 90000 +      # 80-100k
        row[7] * 112500 +     # 100-125k
        row[8] * 137500 +     # 125-150k
        row[9] * 175000 +     # 150-200k
        row[10] * 250000      # 200k+
    )
    avg_income = weighted_income / total_households
    estimated_voters = total_households * 2.5
    turnout_rate = (votes / estimated_voters) * 100
    
    data.append((ward, avg_income, turnout_rate))


fig, ax = plt.subplots(figsize=(12, 7))

incomes = [i[1] for i in data]
turnout = [t[2] for t in data]


ax.scatter(incomes, turnout, s=120, alpha=0.6, color='steelblue', edgecolors='black', linewidth=0.5)


z = np.polyfit(incomes, turnout, 1)
p = np.poly1d(z)
ax.plot(sorted(incomes), p(sorted(incomes)), "r--", linewidth=2, alpha=0.7)

ax.set_xlabel('Average Household Income ($)', fontsize=12)
ax.set_ylabel('Voter Turnout Rate (%)', fontsize=12)
ax.set_title('Do Differences in Average Household Income Lead to a Higher Likelihood of Voting?', fontsize=14)
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.show()

# 14. WHICH MAYOR CANDIDATES APPEAL TO LOWER AND HIGHER AVERAGE HOUSEHOLD INCOMES?

cursor.execute("""
    SELECT DISTINCT
        er."CandidateName",
        hi."Under_$20000" + hi."$20000_to_$39999" + hi."$40000_to_$59999" + 
        hi."$60000_to_$79999" + hi."$80000_to_$99999" + hi."$100000_to_$124999" +
        hi."$125000_to_$149999" + hi."$150000_to_$199999" + hi."$200000_and_over" AS TotalHouseholds,
        hi."Under_$20000",
        hi."$20000_to_$39999",
        hi."$40000_to_$59999",
        hi."$60000_to_$79999",
        hi."$80000_to_$99999",
        hi."$100000_to_$124999",
        hi."$125000_to_$149999",
        hi."$150000_to_$199999",
        hi."$200000_and_over",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_household_income" hi
        ON CAST(REPLACE(hi."Ward", 'WARD ', '') AS INT) = er."Ward"::INT
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", hi."Under_$20000", hi."$20000_to_$39999", hi."$40000_to_$59999",
             hi."$60000_to_$79999", hi."$80000_to_$99999", hi."$100000_to_$124999",
             hi."$125000_to_$149999", hi."$150000_to_$199999", hi."$200000_and_over"
    ORDER BY TotalVotes DESC;
""")

results = cursor.fetchall()


candidate_total_votes = {}
for row in results:
    candidate = row[0]
    votes = row[11]
    if candidate in candidate_total_votes:
        candidate_total_votes[candidate] += votes
    else:
        candidate_total_votes[candidate] = votes


top_5_candidates = sorted(candidate_total_votes.items(), key=lambda x: x[1], reverse=True)[:5]
top_5_names = [item[0] for item in top_5_candidates]


candidate_data = {candidate: [] for candidate in top_5_names}
for row in results:
    candidate = row[0]
    if candidate not in top_5_names:
        continue
        
    total_households = row[1]
    votes = row[11]
    
   
    weighted_income = (
        row[2] * 10000 +      # under 20k
        row[3] * 30000 +      # 20-40k
        row[4] * 50000 +      # 40-60k
        row[5] * 70000 +      # 60-80k
        row[6] * 90000 +      # 80-100k
        row[7] * 112500 +     # 100-125k
        row[8] * 137500 +     # 125-150k
        row[9] * 175000 +     # 150-200k
        row[10] * 250000      # 200k+
    )
    avg_income = weighted_income / total_households
    candidate_data[candidate].append((avg_income, votes))

fig, ax = plt.subplots(figsize=(14, 7))
for candidate, data in candidate_data.items():
    avg_incomes = [item[0] for item in data]
    votes = [item[1] for item in data]
    ax.scatter(avg_incomes, votes, label=candidate, alpha=0.7, s=100)

ax.set_xlabel("Average Household Income ($)")
ax.set_ylabel("Votes Received")
ax.set_title("How Do Top 5 Mayoral Candidates Perform Across Household Income Levels?")
ax.legend(bbox_to_anchor=(1, 1))
ax.set_xlim(80000, 140000)
plt.tight_layout()
plt.show()



# --------------------------------------- _WARD_REC_FACILITIES CHARACTERISTICS -----------------------------------

# 15. DO WARDS WITH MORE RECREATIONAL FACILITIES HAVE HIGHER VOTER TURNOUT? DO PIE CHART

cursor.execute("""
    SELECT
        rf."Ward",
        rf."Total",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_rec_facilities" rf
    LEFT JOIN "_ward_election_results" er
        ON rf."Ward" = er."Ward"
    GROUP BY rf."Ward", rf."Total"
    ORDER BY rf."Ward";
""")

results = cursor.fetchall()
wards = [row[0] for row in results]
recreation_facilities = [row[1] for row in results]
total_votes = [row[2] for row in results]

fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(recreation_facilities, total_votes, s=np.array(recreation_facilities)*10, alpha=0.5, color='purple')
ax.set_xlabel('Number of Recreational Facilities')
ax.set_ylabel('Total Votes')
ax.set_title('Do Wards with More Recreational Facilities Have Higher Voter Turnout?')
ax.set_xticks(range(0, max(recreation_facilities) + 3, 2))
plt.tight_layout()
plt.show()




# 16. WHICH MAYOR CANDIDATES APPEAL TO WARDS WITH MORE RECREATIONAL FACILITIES?

cursor.execute("""
    SELECT
        er."CandidateName",
        rf."Total" AS RecreationFacilities,
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_rec_facilities" rf
        ON er."Ward" = rf."Ward"
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", rf."Total"
    ORDER BY rf."Total", TotalVotes DESC;
""")    
results = cursor.fetchall()

facility_levels = sorted(list(set(row[1] for row in results)))
candidates = sorted(list(set(row[0] for row in results)))


vote_matrix = np.zeros((len(candidates), len(facility_levels)))

for row in results:
    candidate_idx = candidates.index(row[0])
    facility_idx = facility_levels.index(row[1])
    vote_matrix[candidate_idx][facility_idx] = row[2]

fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(vote_matrix, cmap='YlOrRd', aspect='auto')

ax.set_xticks(np.arange(len(facility_levels)))
ax.set_yticks(np.arange(len(candidates)))
ax.set_xticklabels(facility_levels)
ax.set_yticklabels(candidates)

ax.set_xlabel('Number of Recreational Facilities')
ax.set_ylabel('Candidate')
ax.set_title('Which Mayor Candidates Appeal to Wards with Different Amount Recreational Facilities?')

plt.colorbar(im, ax=ax, label='Total Votes')
plt.tight_layout()
plt.show()

# -----------------------------------------  _WARD_TRANSIT_STOPS CHARACTERISTICS -----------------------------------



# 17. DO WARDS WITH ACTIVE TRANSIT STOPS HAVE HIGHER VOTER TURNOUT? 

cursor.execute("""
    SELECT
        ts."ward_num"::INTEGER,
        ts."active_stops",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_transit_stops" ts
    LEFT JOIN "_ward_election_results" er
        ON ts."ward_num"::INTEGER = er."Ward"
    GROUP BY ts."ward_num"::INTEGER, ts."active_stops"
    ORDER BY ts."ward_num"::INTEGER;
""")


results = cursor.fetchall()
wards = [row[0] for row in results]
active_stops = [row[1] for row in results]
total_votes = [row[2] for row in results]

fig, ax = plt.subplots(figsize=(12, 6))
ax.scatter(active_stops, total_votes, s=100, alpha=0.6, color='teal')


z = np.polyfit(active_stops, total_votes, 1)
p = np.poly1d(z)
ax.plot(active_stops, p(active_stops), "r--", linewidth=2)

correlation = np.corrcoef(active_stops, total_votes)[0, 1]

ax.set_xlabel('Number of Active Transit Stops')
ax.set_ylabel('Total Votes')
ax.set_title(f'Do Wards with Active Transit Stops Have Higher Voter Turnout?')
plt.tight_layout()
plt.show()

# 18. WHICH MAYOR CANDIDATES APPEAL TO WARDS WITH MORE ACTIVE TRANSIT STOPS?

cursor.execute("""
    SELECT 
        er."CandidateName",
        ts."active_stops",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_transit_stops" ts
        ON er."Ward" = ts."ward_num"::INTEGER
    WHERE er."OfficeType" = 'MAYOR'
    GROUP BY er."CandidateName", ts."active_stops"
    ORDER BY ts."active_stops", TotalVotes DESC;
""")

results = cursor.fetchall()

candidate_totals = {}
for row in results:
    candidate = row[0]
    votes = row[2]
    candidate_totals[candidate] = candidate_totals.get(candidate, 0) + votes

top_5_candidates = sorted(candidate_totals.items(), key=lambda x: x[1], reverse=True)[:5]
top_5_names = [candidate[0] for candidate in top_5_candidates]


filtered_results = [row for row in results if row[0] in top_5_names]
transit_levels = sorted(list(set(row[1] for row in filtered_results)))
candidate_data = {candidate: [] for candidate in top_5_names}

for row in filtered_results:
    candidate = row[0]
    active_stops = row[1]
    votes = row[2]
    candidate_data[candidate].append((active_stops, votes))

fig, ax = plt.subplots(figsize=(14, 7))
for candidate, data in candidate_data.items():
    data_sorted = sorted(data, key=lambda x: x[0])
    active_stops = [item[0] for item in data_sorted]
    votes = [item[1] for item in data_sorted]
    ax.plot(active_stops, votes, marker='o', label=candidate, linewidth=2.5, markersize=8)

ax.set_xlabel('Number of Active Transit Stops')
ax.set_ylabel('Total Votes')
ax.set_title('How do the Top 5 Mayor Candidates Appeal to Wards with Active Transit Stops?')
ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.show()

# ------------------------------- _WARD_WORK_TRANSPORT CHARACTERISTICS -----------------------------------

# 19. IS THERE A CORRELATION BETWEEN WARDS WITH HIGH PUBLIC TRANSPORT USAGE AND VOTER TURNOUT?

cursor.execute("""
    SELECT
        wt."Ward",
        wt."Number" AS PublicTransitUsers,
        wt."Percent" AS PublicTransitPercent,
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_work_transport" wt
    LEFT JOIN "_ward_election_results" er
        ON wt."Ward" = er."Ward"
    WHERE wt."Mode" = 'Public transit'
    GROUP BY wt."Ward", wt."Number", wt."Percent"
    ORDER BY wt."Ward";
""")

results = cursor.fetchall()
wards = [f"Ward {row[0]}" for row in results]
transit_users = [row[1] for row in results]  
total_votes = [row[3] for row in results]

fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(transit_users, total_votes, s=150, alpha=0.6, color='green')


z = np.polyfit(transit_users, total_votes, 1)
p = np.poly1d(z)
ax.plot(transit_users, p(transit_users), "r--", linewidth=2)

correlation = np.corrcoef(transit_users, total_votes)[0, 1]

ax.set_xlabel('Number of Public Transit Users')
ax.set_ylabel('Total Votes')
ax.set_title('Does Public Transit Usage Result in Higher Voter Turnout?')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# 20. WHICH MAYOR CANDIDATES APPEAL TO WARDS WITH DIFFERENT MODES OF TRANSPORT?

cursor.execute("""
    SELECT
        er."CandidateName",
        wt."Number",
        SUM(REPLACE(er."Votes", ',', '')::INT) AS TotalVotes
    FROM "_ward_election_results" er
    JOIN "_ward_work_transport" wt
        ON er."Ward" = wt."Ward"
    WHERE er."OfficeType" = 'MAYOR' AND wt."Mode" = 'Public transit'
    GROUP BY er."CandidateName", wt."Number"
    ORDER BY TotalVotes DESC;
""")

results = cursor.fetchall()


candidate_totals = {}
for row in results:
    candidate = row[0]
    votes = row[2]
    candidate_totals[candidate] = candidate_totals.get(candidate, 0) + votes

top_5_candidates = sorted(candidate_totals.items(), key=lambda x: x[1], reverse=True)[:5]
top_5_names = [candidate[0] for candidate in top_5_candidates]
filtered_results = [row for row in results if row[0] in top_5_names]
candidate_data = {candidate: {'x': [], 'y': []} for candidate in top_5_names}

for row in filtered_results:
    candidate = row[0]
    transit_users = row[1]
    votes = row[2]
    candidate_data[candidate]['x'].append(transit_users)
    candidate_data[candidate]['y'].append(votes)


fig, ax = plt.subplots(figsize=(12, 6))

for candidate in top_5_names:
    ax.scatter(candidate_data[candidate]['x'], 
              candidate_data[candidate]['y'], 
              label=candidate, 
              alpha=0.7, 
              s=100)

ax.set_xlabel('Number of Public Transit Commuters')
ax.set_ylabel('Total Votes')
ax.set_title('Out of the top 5 Mayor Candidates, what appeal do each of them have to Wards with Public Transit Commuters?')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()