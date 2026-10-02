from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.database import create_tables, initialize_slots
from backend.parking import vehicle_entry, vehicle_exit, get_connection
from backend.simulator import simulate_sensor_reading


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="Smart Parking Management System",
    description="REST API for managing parking slots, vehicles, sensors, and parking sessions.",
    version="1.0.0"
)


# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Database Initialization
# ==========================================

create_tables()
initialize_slots()


# ==========================================
# Request Models
# ==========================================

class VehicleEntryRequest(BaseModel):
    vehicle_number: str
    vehicle_type: str


class VehicleExitRequest(BaseModel):
    vehicle_number: str


class SensorUpdateRequest(BaseModel):
    slot_number: str


# ==========================================
# Root
# ==========================================

@app.get("/")
def root():

    return {
        "message": "Smart Parking Management System API",
        "status": "running"
    }


# ==========================================
# API Status
# ==========================================

@app.get("/api/status")
def api_status():

    return {
        "status": "online",
        "service": "Smart Parking Management System"
    }


# ==========================================
# Parking Slots
# ==========================================

@app.get("/api/slots")
def get_slots():

    connection = get_connection()

    slots = connection.execute(
        """
        SELECT *
        FROM parking_slots
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return {
        "total_slots": len(slots),
        "slots": [dict(slot) for slot in slots]
    }


# ==========================================
# Vehicle Entry
# ==========================================

@app.post("/api/vehicle/entry")
def vehicle_entry_api(
    request: VehicleEntryRequest
):

    result = vehicle_entry(
        request.vehicle_number,
        request.vehicle_type
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


# ==========================================
# Vehicle Exit
# ==========================================

@app.post("/api/vehicle/exit")
def vehicle_exit_api(
    request: VehicleExitRequest
):

    result = vehicle_exit(
        request.vehicle_number
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


# ==========================================
# Statistics
# ==========================================

@app.get("/api/statistics")
def get_statistics():

    connection = get_connection()

    total_slots = connection.execute(
        """
        SELECT COUNT(*)
        FROM parking_slots
        """
    ).fetchone()[0]

    occupied_slots = connection.execute(
        """
        SELECT COUNT(*)
        FROM parking_slots
        WHERE status = 'OCCUPIED'
        """
    ).fetchone()[0]

    available_slots = connection.execute(
        """
        SELECT COUNT(*)
        FROM parking_slots
        WHERE status = 'AVAILABLE'
        """
    ).fetchone()[0]

    total_vehicles = connection.execute(
        """
        SELECT COUNT(*)
        FROM vehicles
        """
    ).fetchone()[0]

    total_revenue = connection.execute(
        """
        SELECT COALESCE(SUM(fee), 0)
        FROM parking_sessions
        WHERE status = 'COMPLETED'
        """
    ).fetchone()[0]

    connection.close()

    occupancy_rate = 0

    if total_slots > 0:

        occupancy_rate = round(
            (occupied_slots / total_slots) * 100,
            2
        )

    return {
        "total_slots": total_slots,
        "available_slots": available_slots,
        "occupied_slots": occupied_slots,
        "occupancy_rate": occupancy_rate,
        "total_vehicles": total_vehicles,
        "total_revenue": total_revenue
    }


# ==========================================
# Parking Sessions
# ==========================================

@app.get("/api/sessions")
def get_sessions():

    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            parking_sessions.id,
            vehicles.vehicle_number,
            vehicles.vehicle_type,
            parking_slots.slot_number,
            parking_sessions.entry_time,
            parking_sessions.exit_time,
            parking_sessions.duration,
            parking_sessions.fee,
            parking_sessions.status
        FROM parking_sessions
        JOIN vehicles
            ON parking_sessions.vehicle_id = vehicles.id
        JOIN parking_slots
            ON parking_sessions.slot_id = parking_slots.id
        ORDER BY parking_sessions.id DESC
        """
    ).fetchall()

    connection.close()

    return {
        "sessions": [dict(session) for session in sessions]
    }


# ==========================================
# Vehicle Search
# ==========================================

@app.get("/api/vehicle/{vehicle_number}")
def get_vehicle(vehicle_number: str):

    connection = get_connection()

    vehicle = connection.execute(
        """
        SELECT
            id,
            vehicle_number,
            vehicle_type
        FROM vehicles
        WHERE UPPER(vehicle_number) = UPPER(?)
        """,
        (vehicle_number,)
    ).fetchone()

    if vehicle is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    session = connection.execute(
        """
        SELECT
            parking_sessions.id,
            parking_slots.slot_number,
            parking_sessions.entry_time,
            parking_sessions.exit_time,
            parking_sessions.duration,
            parking_sessions.fee,
            parking_sessions.status
        FROM parking_sessions
        JOIN parking_slots
            ON parking_sessions.slot_id = parking_slots.id
        WHERE parking_sessions.vehicle_id = ?
        ORDER BY parking_sessions.id DESC
        LIMIT 1
        """,
        (vehicle["id"],)
    ).fetchone()

    connection.close()

    result = {
        "vehicle_number": vehicle["vehicle_number"],
        "vehicle_type": vehicle["vehicle_type"]
    }

    if session:

        result.update({
            "slot_number": session["slot_number"],
            "entry_time": session["entry_time"],
            "exit_time": session["exit_time"],
            "duration": session["duration"],
            "fee": session["fee"],
            "status": session["status"]
        })

    else:

        result.update({
            "slot_number": None,
            "entry_time": None,
            "exit_time": None,
            "duration": None,
            "fee": None,
            "status": "NO PARKING SESSION"
        })

    return result


# ==========================================
# Sensor Update
# ==========================================

@app.post("/api/sensor/update")
def sensor_update(
    request: SensorUpdateRequest
):

    result = simulate_sensor_reading(
        request.slot_number
    )

    if not result["success"]:

        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result