# CPSC471P
### Authors: Sam Safe, Aniket Bulusu, Sultan Alzoghaibi

# Calgary Ward Dashboard

Refer to documents and diagrams sub-folders for other submission-relevant data. You will find our document on normalization under /documents. 

### Requirements:

- Docker Desktop (includes Docker Compose)
  - **Windows/Mac**: Download from https://www.docker.com/products/docker-desktop/
  - **Linux**: Install Docker Engine and Docker Compose plugin 

## Set-up

**Prerequisites:**

Ensure Docker Desktop is installed and **running** 


**Installation:**

Clone the project and navigate into the folder:
```bash
git clone 
cd cpsc471p
```

Then follow these steps:

1. **Start containers:**
   ```bash
   docker compose up --build
   ```

   *Note: First build will take upwards of 120 seconds. Please be patient.*

2. **Open dashboard:**
   ```
   http://localhost:8050
   ```

**Manual data reload (only if needed):**

If you need to reload the data manually:
```bash
docker compose exec app python app/loader.py
```

### Shut-down

```bash
docker compose down
```
Or simply stop the containers with `Ctrl-C` in the terminal running docker compose.

### Troubleshooting

**Docker Desktop not running:**
- **Error**: `error during connect` or `cannot connect to the Docker daemon`
- **Solution**: Docker desktop has to be running - run it and wait for it to initialize.

**Database does not load properly:**

If the database does not load properly, it may have hit an error on a previous build. To get a fresh start:
```bash
docker compose down -v
docker compose up --build
```

The data loader will run automatically when the containers start.

**Timing issues:**

Our database is quite large, and it may take a while to load. If the app loads before the database is populated, it will appear as if there is no data.

Solution - restart the app container:
```bash
docker compose restart app
```

**Permission errors on Windows:**
- You may need to run windows terminal as Administrator

# Tech Stack

### **Infrastructure**
- **Docker** 
- **Docker Compose** 
- **PostgreSQL** 

### **Backend & Database**
- **Python** 
- **SQLAlchemy** 
- **psycopg2-binary** 

### **Web Framework & Visualization**
- **Dash** - web applications framework
- **Plotly** - graphing library
- **Dash Bootstrap Components** - UI components
- **Folium** - web mapping and geospatial visualization

### **Data Processing & Analysis**
- **Pandas** - manipulation, transformation, and analysis
- **GeoPandas** - geographic analysis
- **Shapely** - ward boundaries 
- **statsmodels** - modeling

### **Database Architecture**
- **18 Tables** - some semi-normalized
- **Automated Schema Initialization** - SQL scripts executed on container startup

# Manual Setup (Without Docker)

### **Step 1: Install PostgreSQL**
- Download and install PostgreSQL
- During installation, set a password for the `postgres` superuser

### **Step 2: Create Database and User**
Open pgAdmin and execute:

```sql
CREATE DATABASE calgary_ward_db;
CREATE USER appuser WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE calgary_ward_db TO appuser;
```

### **Step 3: Initialize Database Schema**
Run the schema file to create all tables:

```bash
psql -U appuser -d calgary_ward_db -f db/schema.sql
```

Password is: `app_password`

### **Step 4: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 5: Load Data into Database**
```bash
python app/loader.py
```

### **Step 6: Run the Application**
```bash
python app/app.py
```

### **Step 7: Access Dashboard**
Open your browser to:
```
http://localhost:8050
```

## Important Notes for Manual Setup:

- **Database credentials**: Database is hard coded to use - `appuser/app_password` credentials

# REFERENCES

1. NeuralNine. (2024, September 13). Build Data Apps in Python with Plotly Dash. YouTube. https://www.youtube.com/watch?v=pLU7ZLPhyX8 

2. Colgan, M. (2020, July 7). Developing and Deploying Data-Driven Apps. YouTube. https://www.youtube.com/watch?v=KreNYemH198 

3. Hello dash. Plotly. (n.d.). https://dash.plotly.com/layout 

4. Guides. Docker Documentation. (2024, December 20). https://docs.docker.com/guides/ 

5. PostgreSQL 18.1 documentation. PostgreSQL Documentation. (2025, November 13). https://www.postgresql.org/docs/current/index.html 

6. SQLALCHEMY 2.0 documentation. SQLAlchemy Unified Tutorial - SQLAlchemy 2.0 Documentation. (n.d.). https://docs.sqlalchemy.org/en/20/tutorial/index.html 

7. mCoding. (2024, August 2). Docker Tutorial for Beginners. YouTube. https://www.youtube.com/watch?v=b0HMimUb4f0 

8. A practical introduction to databases — a practical introduction to databases. (n.d.). https://runestone.academy/ns/books/published/practical_db/index.html 

9. W3schools.com. W3Schools Online Web Tutorials. (n.d.-a). https://www.w3schools.com/postgresql/index.php 

10. Ark Coding. (n.d.). Streamlit vs Dash - Which one is better? Interactive Dashboard with Python. YouTube. https://www.youtube.com/watch?v=tXHXDRog37A 

