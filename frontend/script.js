
const API_BASE_URL = "http://127.0.0.1:8000";


// ==========================================
// Utility Functions
// ==========================================

function formatDateTime(value) {

    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IN", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "numeric",
        minute: "2-digit"
    });
}


function showMessage(elementId, message, type) {

    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;

    element.className = `message ${type}`;
}


function clearMessage(elementId) {

    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.className = "message";
}


// ==========================================
// API Helper
// ==========================================

async function apiRequest(endpoint, options = {}) {

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        }
    );


    let data;

    try {

        data = await response.json();

    } catch {

        data = {};
    }


    if (!response.ok) {

        const message =
            data.detail ||
            data.message ||
            "Request failed.";

        throw new Error(message);
    }


    return data;
}


// ==========================================
// System Status
// ==========================================

async function checkSystemStatus() {

    const statusText =
        document.getElementById("systemStatus");

    const statusDot =
        document.getElementById("statusDot");


    try {

        await apiRequest("/api/status");

        statusText.textContent = "System Online";

        statusDot.style.background = "#16a34a";

    } catch {

        statusText.textContent = "System Offline";

        statusDot.style.background = "#dc2626";
    }
}


// ==========================================
// Dashboard Statistics
// ==========================================

async function loadDashboard() {

    try {

        const data =
            await apiRequest("/api/statistics");


        document.getElementById("totalSlots").textContent =
            data.total_slots;


        document.getElementById("availableSlots").textContent =
            data.available_slots;


        document.getElementById("occupiedSlots").textContent =
            data.occupied_slots;


        document.getElementById("occupancyRate").textContent =
            `${data.occupancy_rate}%`;


        document.getElementById("totalRevenue").textContent =
            `₹${Number(data.total_revenue || 0).toFixed(2)}`;


    } catch (error) {

        console.error(
            "Unable to load dashboard:",
            error
        );
    }
}


// ==========================================
// Parking Slots
// ==========================================

async function loadSlots() {

    const parkingGrid =
        document.getElementById("parkingGrid");


    try {

        const data =
            await apiRequest("/api/slots");


        parkingGrid.innerHTML = "";


        data.slots.forEach(slot => {

            const slotElement =
                document.createElement("div");


            const status =
                slot.status === "OCCUPIED"
                    ? "occupied"
                    : "available";


            const statusText =
                slot.status === "OCCUPIED"
                    ? "Occupied"
                    : "Available";


            slotElement.className =
                `parking-slot ${status}`;


            slotElement.innerHTML = `

                <div class="slot-number">
                    ${slot.slot_number}
                </div>

                <div class="slot-status">
                    ${statusText}
                </div>

            `;


            parkingGrid.appendChild(slotElement);

        });


    } catch (error) {

        parkingGrid.innerHTML = `

            <div class="loading">

                Unable to load parking slots.

            </div>

        `;

        console.error(
            "Unable to load slots:",
            error
        );
    }
}


// ==========================================
// Vehicle Entry
// ==========================================

async function handleVehicleEntry(event) {

    event.preventDefault();


    const vehicleNumber =
        document
            .getElementById("entryVehicleNumber")
            .value
            .trim()
            .toUpperCase();


    const vehicleType =
        document
            .getElementById("entryVehicleType")
            .value;


    if (!vehicleNumber) {

        showMessage(
            "entryMessage",
            "Please enter a vehicle number.",
            "error"
        );

        return;
    }


    try {

        const data =
            await apiRequest(
                "/api/vehicle/entry",
                {
                    method: "POST",

                    body: JSON.stringify({
                        vehicle_number: vehicleNumber,
                        vehicle_type: vehicleType
                    })
                }
            );


        showMessage(
            "entryMessage",
            `${data.message} Slot: ${data.slot_number}`,
            "success"
        );


        document
            .getElementById("entryForm")
            .reset();


        await refreshDashboard();


    } catch (error) {

        showMessage(
            "entryMessage",
            error.message,
            "error"
        );
    }
}


// ==========================================
// Vehicle Exit
// ==========================================

async function handleVehicleExit(event) {

    event.preventDefault();


    const vehicleNumber =
        document
            .getElementById("exitVehicleNumber")
            .value
            .trim()
            .toUpperCase();


    if (!vehicleNumber) {

        showMessage(
            "exitMessage",
            "Please enter a vehicle number.",
            "error"
        );

        return;
    }


    try {

        const data =
            await apiRequest(
                "/api/vehicle/exit",
                {
                    method: "POST",

                    body: JSON.stringify({
                        vehicle_number: vehicleNumber
                    })
                }
            );


        showMessage(
            "exitMessage",
            `${data.message} Fee: ₹${Number(data.fee || 0).toFixed(2)}`,
            "success"
        );


        document
            .getElementById("exitForm")
            .reset();


        await refreshDashboard();


    } catch (error) {

        showMessage(
            "exitMessage",
            error.message,
            "error"
        );
    }
}


// ==========================================
// Vehicle Search
// ==========================================

async function handleVehicleSearch(event) {

    event.preventDefault();


    const vehicleNumber =
        document
            .getElementById("searchVehicleNumber")
            .value
            .trim()
            .toUpperCase();


    const resultContainer =
        document.getElementById(
            "vehicleSearchResult"
        );


    clearMessage("searchMessage");


    if (!vehicleNumber) {

        showMessage(
            "searchMessage",
            "Please enter a vehicle number.",
            "error"
        );

        return;
    }


    resultContainer.innerHTML = `

        <div class="loading">

            Searching vehicle...

        </div>

    `;


    try {

        const data =
            await apiRequest(
                `/api/vehicle/${encodeURIComponent(vehicleNumber)}`
            );


        const statusClass =
            data.status === "ACTIVE"
                ? "active"
                : "completed";


        resultContainer.innerHTML = `

            <div class="vehicle-result-header">

                <div>

                    <span class="result-label">
                        Vehicle Number
                    </span>

                    <h3>
                        ${data.vehicle_number}
                    </h3>

                </div>

                <span
                    class="session-status ${statusClass}"
                >
                    ${data.status}
                </span>

            </div>


            <div class="vehicle-result-grid">


                <div class="result-item">

                    <span>
                        Vehicle Type
                    </span>

                    <strong>
                        ${data.vehicle_type || "-"}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        Parking Slot
                    </span>

                    <strong>
                        ${data.slot_number || "-"}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        Entry Time
                    </span>

                    <strong>
                        ${formatDateTime(data.entry_time)}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        Exit Time
                    </span>

                    <strong>
                        ${formatDateTime(data.exit_time)}
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        Duration
                    </span>

                    <strong>
                        ${
                            data.duration !== null &&
                            data.duration !== undefined
                                ? `${data.duration} hrs`
                                : "-"
                        }
                    </strong>

                </div>


                <div class="result-item">

                    <span>
                        Parking Fee
                    </span>

                    <strong>
                        ₹${Number(data.fee || 0).toFixed(2)}
                    </strong>

                </div>


            </div>

        `;


    } catch (error) {

        resultContainer.innerHTML = `

            <div class="result-placeholder">

                <div class="result-placeholder-icon">
                    ⚠️
                </div>

                <p>
                    ${error.message}
                </p>

            </div>

        `;

    }
}


// ==========================================
// Parking Sessions
// ==========================================

async function loadSessions() {

    const table =
        document.getElementById(
            "sessionsTable"
        );


    try {

        const data =
            await apiRequest("/api/sessions");


        if (
            !data.sessions ||
            data.sessions.length === 0
        ) {

            table.innerHTML = `

                <tr>

                    <td
                        colspan="8"
                        class="loading"
                    >
                        No parking sessions found.
                    </td>

                </tr>

            `;

            return;
        }


        table.innerHTML = "";


        data.sessions.forEach(session => {

            const row =
                document.createElement("tr");


            const statusClass =
                session.status === "ACTIVE"
                    ? "active"
                    : "completed";


            row.innerHTML = `

                <td>
                    <strong>
                        ${session.vehicle_number}
                    </strong>
                </td>

                <td>
                    ${session.vehicle_type || "-"}
                </td>

                <td>
                    ${session.slot_number || "-"}
                </td>

                <td>
                    ${formatDateTime(session.entry_time)}
                </td>

                <td>
                    ${formatDateTime(session.exit_time)}
                </td>

                <td>
                    ${
                        session.duration !== null &&
                        session.duration !== undefined
                            ? `${session.duration} hrs`
                            : "-"
                    }
                </td>

                <td>
                    ₹${Number(session.fee || 0).toFixed(2)}
                </td>

                <td>

                    <span
                        class="session-status ${statusClass}"
                    >
                        ${session.status}
                    </span>

                </td>

            `;


            table.appendChild(row);

        });


    } catch (error) {

        table.innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="loading"
                >
                    Unable to load parking sessions.
                </td>

            </tr>

        `;

        console.error(
            "Unable to load sessions:",
            error
        );
    }
}


// ==========================================
// Refresh Everything
// ==========================================

async function refreshDashboard() {

    await Promise.all([
        loadDashboard(),
        loadSlots(),
        loadSessions(),
        checkSystemStatus()
    ]);
}


// ==========================================
// Form Event Listeners
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const entryForm =
            document.getElementById(
                "entryForm"
            );


        const exitForm =
            document.getElementById(
                "exitForm"
            );


        const searchForm =
            document.getElementById(
                "searchForm"
            );


        if (entryForm) {

            entryForm.addEventListener(
                "submit",
                handleVehicleEntry
            );

        }


        if (exitForm) {

            exitForm.addEventListener(
                "submit",
                handleVehicleExit
            );

        }


        if (searchForm) {

            searchForm.addEventListener(
                "submit",
                handleVehicleSearch
            );

        }


        refreshDashboard();


        // Automatic dashboard refresh
        setInterval(
            refreshDashboard,
            10000
        );

    }
);

