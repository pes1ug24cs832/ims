"""SQLite storage module for the Inventory Management System."""
import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from .config import DB_PATH

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_type TEXT CHECK(order_type IN ('SALE', 'PURCHASE')) NOT NULL,
    product_sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_sku) REFERENCES products(sku)
);

CREATE TABLE IF NOT EXISTS admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

class DatabaseError(Exception):
    """Raised when a database operation fails."""
    pass

class Database:
    """SQLite database wrapper with connection management."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
        self.connection: Optional[sqlite3.Connection] = None

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def connect(self) -> None:
        """Create a database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            # Enable foreign key support
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._create_schema()
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Database connection failed: {e}")

    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _create_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        if not self.connection:
            raise DatabaseError("No database connection")
        try:
            self.connection.executescript(SCHEMA_SQL)
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create schema: {e}")
            raise DatabaseError(f"Schema creation failed: {e}")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query and return the cursor."""
        if not self.connection:
            raise DatabaseError("No database connection")
        try:
            return self.connection.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query execution failed: {e}")

    def execute_many(self, query: str, params: List[tuple]) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets."""
        if not self.connection:
            raise DatabaseError("No database connection")
        try:
            return self.connection.executemany(query, params)
        except sqlite3.Error as e:
            logger.error(f"Batch query execution failed: {e}")
            raise DatabaseError(f"Batch query execution failed: {e}")

    def commit(self) -> None:
        """Commit the current transaction."""
        if not self.connection:
            raise DatabaseError("No database connection")
        try:
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to commit transaction: {e}")
            raise DatabaseError(f"Transaction commit failed: {e}")

    def rollback(self) -> None:
        """Rollback the current transaction."""
        if not self.connection:
            raise DatabaseError("No database connection")
        try:
            self.connection.rollback()
        except sqlite3.Error as e:
            logger.error(f"Failed to rollback transaction: {e}")
            raise DatabaseError(f"Transaction rollback failed: {e}")

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result row."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and fetch all result rows."""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def __enter__(self) -> 'Database':
        """Context manager enter."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.disconnect()