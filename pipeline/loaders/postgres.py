import os
from pathlib import Path


import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open a connection to the MarketPulse PostgresSQL database."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    return psycopg.connect(database_url)


def initialize_database() -> None:
    """Initialize the database defined in database/schema.sql"""

    project_root = Path(__file__).resolve().parents[2]
    schema_path = project_root / "database" / "schema.sql"

    schema = schema_path.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.execute(schema)
