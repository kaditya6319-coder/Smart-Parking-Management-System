import sqlite3
from datetime import datetime
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "parking.db"


def get_connection():
    """Create a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def find_available_slot():
    """Find the first available parking slot."""

    connection = get_connection()

    slot = connection.execute("""
        SELECT *
        FROM parking_slots
        WHERE status = 'AVAILABLE'
        ORDER BY id
        LIMIT 1
    """).fetchone()

    connection.close()

    return slot


def register_vehicle(vehicle_number, vehicle_type):
    """Register a vehicle if it does not already exist."""

    connection = get_connection()

    vehicle = connection.execute("""
        SELECT *
        FROM vehicles
        WHERE vehicle_number = ?
    """, (vehicle_number,)).fetchone()

    if vehicle:
        connection.close()
        return vehicle

    cursor = connection.execute("""
        INSERT INTO vehicles (vehicle_number, vehicle_type)
        VALUES (?, ?)
    """, (vehicle_number, vehicle_type))

    connection.commit()

    vehicle = connection.execute("""
        SELECT *
        FROM vehicles
        WHERE id = ?
    """, (cursor.lastrowid,)).fetchone()

    connection.close()

    return vehicle


def vehicle_entry(vehicle_number, vehicle_type):
    """Handle vehicle entry and assign an available parking slot."""

    connection = get_connection()

    # Check whether the vehicle is already parked
    vehicle = connection.execute("""
        SELECT *
        FROM vehicles
        WHERE vehicle_number = ?
    """, (vehicle_number,)).fetchone()

    if vehicle:
        active_session = connection.execute("""
            SELECT *
            FROM parking_sessions
            WHERE vehicle_id = ?
            AND status = 'ACTIVE'
        """, (vehicle["id"],)).fetchone()

        if active_session:
            connection.close()

            return {
                "success": False,
                "message": "Vehicle is already parked."
            }

    # Find available slot
    slot = connection.execute("""
        SELECT *
        FROM parking_slots
        WHERE status = 'AVAILABLE'
        ORDER BY id
        LIMIT 1
    """).fetchone()

    if not slot:
        connection.close()

        return {
            "success": False,
            "message": "No parking slots available."
        }

    # Register vehicle if necessary
    if not vehicle:
        cursor = connection.execute("""
            INSERT INTO vehicles (vehicle_number, vehicle_type)
            VALUES (?, ?)
        """, (vehicle_number, vehicle_type))

        vehicle_id = cursor.lastrowid

    else:
        vehicle_id = vehicle["id"]

    # Current entry time
    entry_time = datetime.now().isoformat(timespec="seconds")

    # Create parking session
    connection.execute("""
        INSERT INTO parking_sessions
        (vehicle_id, slot_id, entry_time, status)
        VALUES (?, ?, ?, 'ACTIVE')
    """, (vehicle_id, slot["id"], entry_time))

    # Mark slot as occupied
    connection.execute("""
        UPDATE parking_slots
        SET status = 'OCCUPIED'
        WHERE id = ?
    """, (slot["id"],))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Vehicle parked successfully.",
        "vehicle_number": vehicle_number,
        "slot_number": slot["slot_number"],
        "entry_time": entry_time
    }


def vehicle_exit(vehicle_number):
    """Handle vehicle exit and calculate parking fee."""

    connection = get_connection()

    # Find vehicle
    vehicle = connection.execute("""
        SELECT *
        FROM vehicles
        WHERE vehicle_number = ?
    """, (vehicle_number,)).fetchone()

    if not vehicle:
        connection.close()

        return {
            "success": False,
            "message": "Vehicle not found."
        }

    # Find active parking session
    session = connection.execute("""
        SELECT *
        FROM parking_sessions
        WHERE vehicle_id = ?
        AND status = 'ACTIVE'
    """, (vehicle["id"],)).fetchone()

    if not session:
        connection.close()

        return {
            "success": False,
            "message": "Vehicle is not currently parked."
        }

    # Calculate exit time
    exit_time = datetime.now()

    entry_time = datetime.fromisoformat(session["entry_time"])

    # Calculate duration in hours
    duration_seconds = (exit_time - entry_time).total_seconds()
    duration_hours = max(duration_seconds / 3600, 0)

    # Parking fee
    hourly_rate = 20
    fee = max(20, round(duration_hours * hourly_rate, 2))

    # Update parking session
    connection.execute("""
        UPDATE parking_sessions
        SET exit_time = ?,
            duration = ?,
            fee = ?,
            status = 'COMPLETED'
        WHERE id = ?
    """, (
        exit_time.isoformat(timespec="seconds"),
        round(duration_hours, 2),
        fee,
        session["id"]
    ))

    # Free the parking slot
    connection.execute("""
        UPDATE parking_slots
        SET status = 'AVAILABLE'
        WHERE id = ?
    """, (session["slot_id"],))

    connection.commit()

    # Get slot number
    slot = connection.execute("""
        SELECT slot_number
        FROM parking_slots
        WHERE id = ?
    """, (session["slot_id"],)).fetchone()

    connection.close()

    return {
        "success": True,
        "message": "Vehicle exited successfully.",
        "vehicle_number": vehicle_number,
        "slot_number": slot["slot_number"],
        "duration_hours": round(duration_hours, 2),
        "fee": fee,
        "exit_time": exit_time.isoformat(timespec="seconds")
    }