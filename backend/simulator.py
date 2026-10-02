import sqlite3
from datetime import datetime


DATABASE_PATH = "data/parking.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def simulate_sensor_reading(slot_number):
    """
    Simulates a parking sensor by reading the actual
    parking state from the database.

    The sensor does not randomly modify the database.
    It reports the state already determined by the
    parking management system.
    """

    connection = get_connection()

    slot = connection.execute(
        """
        SELECT id, slot_number, status
        FROM parking_slots
        WHERE slot_number = ?
        """,
        (slot_number.upper(),)
    ).fetchone()

    connection.close()

    if slot is None:

        return {
            "success": False,
            "message": f"Parking slot {slot_number} not found."
        }

    vehicle_detected = (
        slot["status"] == "OCCUPIED"
    )

    return {
        "success": True,
        "slot_number": slot["slot_number"],
        "vehicle_detected": vehicle_detected,
        "status": slot["status"],
        "sensor_time": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def simulate_all_sensors():

    connection = get_connection()

    slots = connection.execute(
        """
        SELECT slot_number, status
        FROM parking_slots
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    results = []

    for slot in slots:

        vehicle_detected = (
            slot["status"] == "OCCUPIED"
        )

        result = {
            "slot_number": slot["slot_number"],
            "vehicle_detected": vehicle_detected,
            "status": slot["status"]
        }

        results.append(result)

        print(
            f"{slot['slot_number']} | "
            f"Vehicle Detected: {vehicle_detected} | "
            f"Status: {slot['status']}"
        )

    return results


if __name__ == "__main__":

    print(
        "Starting parking sensor simulation..."
    )

    print()

    simulate_all_sensors()