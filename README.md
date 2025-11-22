# CPSC471P
### Authors: Sam Safe, Aniket Bulusu, Sultan Alzoghaibi

# Calgary Ward Dashboard

### Requirements:

- Docker
- Docker Compose

### Set-up

Clone the project, and cd into the cloned folder, then...

1. **Start containers:**
```bash
   docker-compose up --build
```

2. **Load data** (in new terminal):
```bash
   docker-compose exec app python app/load_data.py
```

3. **Open dashboard:**
```
   http://localhost:8050
```

### Shut-down

```bash
docker-compose down
```
Or simply crash the program with Ctrl-C.

### Troubleshooting

If database does not load properly, it may have hit an error on a previous build. To get a fresh start:
```bash
docker-compose down -v
docker-compose up --build
docker-compose exec app python app/load_data.py
```

Another possible issue is of timing. Our database is quite large, and it may take a while to load.

If the app loads before the database is populated, it will appear as if there is no data. If this happens:
```bash
docker-compose restart app
```

## Project Structure MUST look like this
```
|-- docker-compose.yml     # docker compose file |--
|-- Dockerfile             # docker container
|-- requirements.txt       # dependencies
|-- entrypoint.sh          # entry script used by docker
|-- diagrams/              # project diagrams
|   |-- (all diagrams are here)
|-- db/                    # data-base relevant items
|   |-- schema.sql         # Database schema (auto-loaded)
|-- app/                   # All python apps go here
|   |-- app.py             # Dash dashboard
|   |-- load_data.py       # ETL script
|   |-- sanitychecker.py   # debugging tool - not relevant to app
|-- datasets/              # CSV files (required!)
    |-- (all project datasets)
```

# Tech Stack

### **Infrastructure**
- **Docker** - Containerization platform
- **PostgreSQL** - Relational database management system

### **Backend**
- **Python** - Core programming language
- **SQLAlchemy** - SQL toolkit for operations
- **psycopg2-binary** - PostgreSQL adapter for Python

### **Web Framework & Visualization**
- **Dash** - Python framework for building analytical web applications
- **Plotl** - Interactive graphing library
- **Dash Bootstrap Components** - Bootstrap components for Dash

### **Data Processing**
- **Pandas** - Data manipulation and analysis
- **Shapely** - Geospatial data processing (ward boundaries)

### **Database Architecture**
- **18 Normalized Tables**