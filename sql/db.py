import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# These match the variable names used in view_schema.ipynb
DB_SERVER = os.environ.get("DB_SERVER", "localhost")
DB_PORT   = os.environ.get("DB_PORT", "1433")
DB_USER   = os.environ.get("DB_USER", "")
DB_PASS   = os.environ.get("DB_PASS", "")
DB_NAME   = os.environ.get("DB_NAME", "NexonDB")
DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# SQLAlchemy 2.0 URL.create for proper mssql+pyodbc formatting
# Port is embedded in the host string for pyodbc
connection_url = URL.create(
    "mssql+pyodbc",
    username=DB_USER,
    password=DB_PASS,
    host=DB_SERVER,
    port=int(DB_PORT),
    database=DB_NAME,
    query={
        "driver": DB_DRIVER,
        "Encrypt": "no",
        "TrustServerCertificate": "YES",
    },
)

# Initialize engine only if credentials are provided — prevents crash on boot without .env
if DB_SERVER and DB_SERVER != "your_server_name" and DB_NAME:
    engine = create_engine(connection_url, pool_size=5, max_overflow=10)
else:
    engine = None

def get_engine():
    if engine is None:
        raise ValueError(
            "Database not configured. Please set DB_SERVER, DB_NAME, DB_USER, DB_PASS in .env"
        )
    return engine

Base = declarative_base()

# Write-capable session factory (used only by interaction_logger)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

def get_session():
    if SessionLocal is None:
        raise ValueError("DB not configured")
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
