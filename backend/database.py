import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DATABASE_PATH = BASE_DIR / "data" / "parking.db"


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Parking slots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'AVAILABLE'
        )
    """)

    # Vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT NOT NULL
        )
    """)

    # Parking sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            duration REAL,
            fee REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ACTIVE',

            FOREIGN KEY (vehicle_id)
                REFERENCES vehicles(id),

            FOREIGN KEY (slot_id)
                REFERENCES parking_slots(id)
        )
    """)

    connection.commit()
    connection.close()


def initialize_slots():
    """Create the initial 10 parking slots."""

    connection = get_connection()
    cursor = connection.cursor()

    for number in range(1, 11):
        slot_number = f"P{number:02d}"

        cursor.execute("""
            INSERT OR IGNORE INTO parking_slots
            (slot_number, status)
            VALUES (?, 'AVAILABLE')
        """, (slot_number,))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    initialize_slots()

    print("Database created successfully.")
    print("10 parking slots initialized.")