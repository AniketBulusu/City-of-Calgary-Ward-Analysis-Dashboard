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

### Troubleshooting

If database does not load properly, it may have hit an error on a previous build. To get a fresh start:
```bash
docker-compose down -v
docker-compose up --build
docker-compose exec app python app/load_data.py
```

## Project Structure MUST look like this
```
├── docker-compose.yml    # docker compose file
├── Dockerfile            # docker container
├── requirements.txt      # dependencies
├── db/
│   └── schema.sql       # Database schema (auto-loaded)
├── app/
│   ├── app.py           # Dash dashboard
│   └── load_data.py     # ETL script
└── datasets/            # CSV files (required!)
    └── (all project datasets)
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