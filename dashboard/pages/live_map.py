import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DASHBOARD_DIR = BASE_DIR / "dashboard"

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Live Emergency Map",
    page_icon="🗺️",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🗺️ Live Emergency Map")

st.caption(
    "Interactive map showing the current emergency "
    "incident and selected response resources."
)


st.divider()


# ============================================================
# IMPORT ONLY AFTER PAGE LOAD CONFIGURATION
# ============================================================

try:

    from app.agents.coordinator_agent import (
        coordinate_emergency
    )

    from components.maps import (
        display_emergency_map
    )

except Exception as error:

    st.error(
        "❌ Required project modules could not be loaded."
    )

    st.exception(error)

    st.stop()


# ============================================================
# LOAD BUTTON
# ============================================================

load_map = st.button(
    "🗺️ Load Live Emergency Map",
    type="primary",
    use_container_width=True,
)


# ============================================================
# INITIAL STATE
# ============================================================

if not load_map:

    st.info(
        "Click **🗺️ Load Live Emergency Map** "
        "to load the latest emergency incident "
        "and selected resources."
    )

    st.markdown(
        """
        ### Map will show

        🔴 Emergency Incident  
        🔵 Selected Ambulance  
        🟢 Selected Hospital  
        🟠 Selected Rescue Team
        """
    )

    st.stop()


# ============================================================
# RUN COORDINATION
# ============================================================

with st.spinner(
    "Loading emergency location data..."
):

    try:

        result = coordinate_emergency()

    except Exception as error:

        st.error(
            "❌ Emergency coordination failed."
        )

        st.exception(error)

        st.stop()


# ============================================================
# SUCCESS
# ============================================================

st.success(
    "✅ Emergency map data loaded successfully."
)


# ============================================================
# CURRENT INCIDENT
# ============================================================

current_incident = result.get(
    "current_incident",
    {}
)


if current_incident:

    st.header(
        "🚨 Current Emergency"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Incident",
            current_incident.get(
                "incident_type",
                "N/A"
            )
        )

    with col2:

        st.metric(
            "Severity",
            current_incident.get(
                "severity",
                "N/A"
            )
        )

    with col3:

        st.metric(
            "Victims",
            current_incident.get(
                "victims",
                0
            )
        )

    with col4:

        st.metric(
            "Critical Victims",
            current_incident.get(
                "critical_victims",
                0
            )
        )

    st.info(
        f"📍 Location: "
        f"{current_incident.get('location', 'N/A')}, "
        f"{current_incident.get('city', 'N/A')}"
    )


# ============================================================
# MAP
# ============================================================

st.header(
    "🗺️ Emergency Resource Map"
)

try:

    display_emergency_map(
        result
    )

except Exception as error:

    st.error(
        "❌ Emergency map could not be displayed."
    )

    st.exception(error)


# ============================================================
# RESOURCE SUMMARY
# ============================================================

st.divider()

st.header(
    "🚨 Selected Emergency Resources"
)


resources = result.get(
    "optimized_resources",
    {}
)

ambulance = resources.get(
    "ambulance"
)

hospital = resources.get(
    "hospital"
)

rescue_team = resources.get(
    "rescue_team"
)


col1, col2, col3 = st.columns(3)


# ============================================================
# AMBULANCE
# ============================================================

with col1:

    st.subheader(
        "🚑 Ambulance"
    )

    if ambulance:

        st.write(
            f"**Vehicle:** "
            f"{ambulance.get('vehicle_number', 'N/A')}"
        )

        distance = ambulance.get(
            "distance_km"
        )

        st.write(
            f"**Distance:** "
            f"{distance:.2f} km"
            if distance is not None
            else "**Distance:** N/A"
        )

    else:

        st.warning(
            "No ambulance available."
        )


# ============================================================
# HOSPITAL
# ============================================================

with col2:

    st.subheader(
        "🏥 Hospital"
    )

    if hospital:

        st.write(
            f"**Hospital:** "
            f"{hospital.get('name', 'N/A')}"
        )

        st.write(
            f"**Available Beds:** "
            f"{hospital.get('available_beds', 'N/A')}"
        )

        distance = hospital.get(
            "distance_km"
        )

        st.write(
            f"**Distance:** "
            f"{distance:.2f} km"
            if distance is not None
            else "**Distance:** N/A"
        )

    else:

        st.warning(
            "No suitable hospital available."
        )


# ============================================================
# RESCUE TEAM
# ============================================================

with col3:

    st.subheader(
        "🚒 Rescue Team"
    )

    if rescue_team:

        st.write(
            f"**Team:** "
            f"{rescue_team.get('team_name', 'N/A')}"
        )

        st.write(
            f"**Type:** "
            f"{rescue_team.get('team_type', 'N/A')}"
        )

        distance = rescue_team.get(
            "distance_km"
        )

        st.write(
            f"**Distance:** "
            f"{distance:.2f} km"
            if distance is not None
            else "**Distance:** N/A"
        )

    else:

        st.warning(
            "No rescue team available."
        )


# ============================================================
# ROUTE
# ============================================================

st.divider()

st.header(
    "🛣️ Emergency Route"
)

route = result.get(
    "route"
)


if route:

    col1, col2 = st.columns(2)

    with col1:

        distance = route.get(
            "distance_km"
        )

        st.metric(
            "Route Distance",
            (
                f"{distance:.2f} km"
                if distance is not None
                else "N/A"
            )
        )

    with col2:

        time_minutes = route.get(
            "time_minutes"
        )

        st.metric(
            "Estimated Travel Time",
            (
                f"{time_minutes:.2f} min"
                if time_minutes is not None
                else "N/A"
            )
        )

else:

    st.warning(
        "⚠️ Emergency route unavailable."
    )