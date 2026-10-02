# Smart Parking Management System

A full-stack Smart Parking Management System designed to manage parking slots, vehicle entry and exit, parking sessions, occupancy, revenue, and sensor-based slot monitoring through a REST API and web dashboard.

## Overview

The system provides a centralized platform for monitoring and managing a parking facility.

It combines:

* **FastAPI** for the backend REST API
* **SQLite** for structured parking and session data
* **HTML, CSS and JavaScript** for the web dashboard
* **Python-based sensor simulation** for parking-slot monitoring

The application automatically assigns available parking slots, records vehicle sessions, calculates parking fees, tracks occupancy, and displays real-time parking information through the dashboard.

---

## Key Features

### Parking Management

* View all parking slots
* Display slot availability in real time
* Automatically assign an available slot during vehicle entry
* Release the slot when a vehicle exits
* Prevent duplicate active parking entries

### Vehicle Management

* Register vehicles during entry
* Store vehicle number and vehicle type
* Search vehicles using their registration number
* View the latest parking session for a vehicle

### Parking Sessions

Each parking session records:

* Vehicle
* Vehicle type
* Assigned parking slot
* Entry time
* Exit time
* Parking duration
* Parking fee
* Session status

### Dashboard Analytics

The dashboard displays:

* Total parking slots
* Available slots
* Occupied slots
* Occupancy rate
* Total revenue
* Parking slot status
* Recent parking sessions

### Sensor Simulation

The system includes a Python-based sensor simulator that can simulate whether a vehicle is detected in a parking slot.

The simulated sensor updates the slot status between:

* `AVAILABLE`
* `OCCUPIED`

---

## Technology Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| Frontend        | HTML5, CSS3, JavaScript |
| Backend         | Python, FastAPI         |
| Database        | SQLite                  |
| API             | REST API                |
| Server          | Uvicorn                 |
| Data Processing | Python                  |
| Version Control | Git                     |
| Repository      | GitHub                  |

---

## System Architecture

```text
                    ┌─────────────────────────┐
                    │     Web Dashboard       │
                    │   HTML + CSS + JS       │
                    └────────────┬────────────┘
                                 │
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend    │
                    │                         │
                    │ Vehicle Management      │
                    │ Parking Management       │
                    │ Statistics               │
                    │ Session Management       │
                    │ Sensor Updates           │
                    └────────────┬────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
        ┌───────────────────┐       ┌────────────────────┐
        │   SQLite Database │       │ Sensor Simulator   │
        │                   │       │      Python        │
        │ Parking Slots     │       │                    │
        │ Vehicles          │       │ Vehicle Detection  │
        │ Parking Sessions  │       │ Slot Status        │
        └───────────────────┘       └────────────────────┘
```

---

## Parking Workflow

```text
Vehicle Arrives
       │
       ▼
Vehicle Entry Request
       │
       ▼
Check Existing Active Session
       │
       ├── Already Parked ──► Reject Request
       │
       ▼
Find Available Slot
       │
       ├── No Slot Available ──► Reject Request
       │
       ▼
Assign Parking Slot
       │
       ▼
Create Active Parking Session
       │
       ▼
Vehicle Parks
       │
       ▼
Vehicle Exit Request
       │
       ▼
Calculate Parking Duration
       │
       ▼
Calculate Parking Fee
       │
       ▼
Complete Parking Session
       │
       ▼
Release Parking Slot
```

---

## Database Design

The system uses SQLite for persistent storage.

### `parking_slots`

Stores information about parking spaces.

| Column        | Description            |
| ------------- | ---------------------- |
| `id`          | Unique slot identifier |
| `slot_number` | Parking slot number    |
| `status`      | Current slot status    |

Example statuses:

```text
AVAILABLE
OCCUPIED
```

### `vehicles`

Stores registered vehicle information.

| Column           | Description                 |
| ---------------- | --------------------------- |
| `id`             | Unique vehicle identifier   |
| `vehicle_number` | Vehicle registration number |
| `vehicle_type`   | Type of vehicle             |

### `parking_sessions`

Stores the parking history of vehicles.

| Field        | Description            |
| ------------ | ---------------------- |
| `id`         | Session identifier     |
| `vehicle_id` | Related vehicle        |
| `slot_id`    | Assigned parking slot  |
| `entry_time` | Vehicle entry time     |
| `exit_time`  | Vehicle exit time      |
| `duration`   | Parking duration       |
| `fee`        | Calculated parking fee |
| `status`     | Session status         |

---

## REST API

The FastAPI backend provides the following endpoints.

### System

```text
GET /
GET /api/status
```

### Parking Slots

```text
GET /api/slots
```

Returns all parking slots and their current status.

### Statistics

```text
GET /api/statistics
```

Returns:

* Total slots
* Available slots
* Occupied slots
* Occupancy rate
* Total vehicles
* Total revenue

### Vehicle Entry

```text
POST /api/vehicle/entry
```

Registers a vehicle and assigns an available parking slot.

Example request:

```json
{
    "vehicle_number": "PB01AB1234",
    "vehicle_type": "Car"
}
```

### Vehicle Exit

```text
POST /api/vehicle/exit
```

Processes a vehicle exit and calculates the parking fee.

Example request:

```json
{
    "vehicle_number": "PB01AB1234"
}
```

### Vehicle Search

```text
GET /api/vehicle/{vehicle_number}
```

Returns the vehicle's latest parking information.

### Parking Sessions

```text
GET /api/sessions
```

Returns parking session history.

### Sensor Update

```text
POST /api/sensor/update
```

Simulates a parking sensor reading.

Example request:

```json
{
    "slot_number": "P03"
}
```

---

## Project Structure

```text
Smart-Parking-Management-System/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── parking.py
│   └── simulator.py
│
├── data/
│   └── parking.db
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── screenshots/
│
├── .gitignore
├── README.md
└── requirements.txt
```

> `parking.db` and the Python virtual environment are excluded from Git using `.gitignore`.

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd Smart-Parking-Management-System
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

### 3. Activate the Virtual Environment

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Initialize the Database

Run:

```powershell
python backend\database.py
```

This creates the SQLite database and initializes the parking slots.

---

## Run the Backend

From the project root:

```powershell
uvicorn backend.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Run the Frontend

Open another PowerShell window and navigate to the project directory:

```powershell
cd "D:\Portfolio\Smart-Parking-Management-System"
```

Then run:

```powershell
python -m http.server 5500 --directory frontend
```

Open the dashboard:

```text
http://127.0.0.1:5500
```

---

## Testing Performed

The following application workflows have been tested successfully:

* Dashboard statistics
* Parking slot display
* Vehicle entry
* Automatic slot assignment
* Duplicate vehicle-entry prevention
* Vehicle exit
* Parking duration calculation
* Parking fee calculation
* Vehicle search
* Parking session history
* Sensor simulation
* Backend API communication
* Frontend-to-backend communication

---

## Example Parking Scenario

```text
Vehicle: PB01AB1234
Type: Car

Entry
  ↓
Available Slot Found
  ↓
Slot Assigned
  ↓
Parking Session Created
  ↓
Vehicle Exits
  ↓
Duration Calculated
  ↓
Fee Calculated
  ↓
Session Completed
  ↓
Slot Released
```

---

## Skills Demonstrated

This project demonstrates practical experience with:

* Python
* FastAPI
* REST APIs
* SQLite
* SQL
* Database design
* CRUD operations
* Backend development
* Frontend development
* JavaScript
* HTML
* CSS
* Data validation
* Business logic
* Parking analytics
* Occupancy calculation
* Revenue calculation
* API integration
* Git and GitHub

---

## Future Enhancements

Potential future improvements include:

* PostgreSQL integration
* User authentication and authorization
* Admin dashboard
* Advanced analytics and reporting
* Real IoT sensor integration
* QR-code based parking entry
* Online parking reservation
* Payment gateway integration
* Automated notifications
* Role-based access control
* Cloud deployment
* Mobile application

---

## Author

**Harshit**

This project was developed as a practical full-stack application demonstrating Python, SQL, REST API development, database management, frontend development, and analytical dashboard concepts.
