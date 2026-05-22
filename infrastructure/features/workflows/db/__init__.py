"""Database initialization for workflows feature"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "workflows.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db():
    """Initialize the workflows database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.close()


@contextmanager
def get_db_connection():
    """Get database connection context manager"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Initialize database on import
init_db()
