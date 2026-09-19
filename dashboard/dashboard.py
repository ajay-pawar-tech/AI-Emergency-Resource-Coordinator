import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


# ============================================================
# IMPORTS
# ============================================================

from app.agents.coordinator_agent import coordinate_emergency
from components.cards import display_emergency_cards
from components.charts import display_emergency_charts
from components.maps import display_emergency_map


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Emergency Resource Coordinator",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HEADER
# ============================================================

st.title("🚨 AI Emergency Resource Coordinator")

st.caption(
    "AI-powered emergency response coordination and resource optimization system"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🚨 Emergency Control")

    st.write(
        "AI-powered system for real-time emergency "
        "incident analysis and resource coordination."
    )

    st.divider()

    st.info(
        "Run the complete emergency coordination workflow "
        "to analyze the current incident, select resources, "
        "calculate route, check weather, and generate an AI recommendation."
    )


# ============================================================
# RUN BUTTON
# ============================================================

run_coordination = st.button(
    "🚨 Run Emergency Coordination",
    type="primary",
    use_container_width=True,
)


# ============================================================
# COORDINATION WORKFLOW
# ============================================================

if run_coordination:

    with st.spinner(
        "Analyzing emergency situation..."
    ):

        try:

            result = coordinate_emergency()

        except Exception as error:

            st.error(
                "❌ Emergency coordination failed."
            )

            st.exception(error)

            st.stop()


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    st.success(
        "✅ Emergency coordination completed successfully."
    )


    # ========================================================
    # CURRENT EMERGENCY
    # ========================================================

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
                "Total Victims",
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


    # ========================================================
    # EXTRACT RESOURCES
    # ========================================================

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

    route = result.get(
        "route"
    )

    weather = result.get(
        "weather",
        {}
    )


    # ========================================================
    # EMERGENCY STATISTICS
    # ========================================================

    st.header(
        "📊 Emergency Statistics"
    )

    display_emergency_cards(
        result
    )


    # ========================================================
    # EMERGENCY ANALYTICS
    # ========================================================

    st.header(
        "📈 Emergency Analytics"
    )

    try:

        display_emergency_charts(
            result
        )

    except Exception as error:

        st.warning(
            "⚠️ Emergency analytics could not be displayed."
        )

        st.exception(error)


    # ========================================================
    # EMERGENCY MAP
    # ========================================================

    st.header(
        "🗺️ Emergency Map"
    )

    try:

        display_emergency_map(
            result
        )

    except Exception as error:

        st.warning(
            "⚠️ Emergency map could not be displayed."
        )

        st.exception(error)


    # ========================================================
    # SELECTED AMBULANCE
    # ========================================================

    st.header(
        "🚑 Selected Ambulance"
    )

    if ambulance:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Vehicle",
                ambulance.get(
                    "vehicle_number",
                    "N/A"
                )
            )

        with col2:

            distance = ambulance.get(
                "distance_km"
            )

            st.metric(
                "Distance",
                (
                    f"{distance:.2f} km"
                    if distance is not None
                    else "N/A"
                )
            )

    else:

        st.warning(
            "⚠️ No ambulance available."
        )


    # ========================================================
    # SELECTED HOSPITAL
    # ========================================================

    st.header(
        "🏥 Selected Hospital"
    )

    if hospital:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Hospital",
                hospital.get(
                    "name",
                    "N/A"
                )
            )

        with col2:

            st.metric(
                "Available Beds",
                hospital.get(
                    "available_beds",
                    "N/A"
                )
            )

        with col3:

            distance = hospital.get(
                "distance_km"
            )

            st.metric(
                "Distance",
                (
                    f"{distance:.2f} km"
                    if distance is not None
                    else "N/A"
                )
            )

    else:

        st.warning(
            "⚠️ No suitable hospital available."
        )


    # ========================================================
    # SELECTED RESCUE TEAM
    # ========================================================

    st.header(
        "🚒 Selected Rescue Team"
    )

    if rescue_team:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Team",
                rescue_team.get(
                    "team_name",
                    "N/A"
                )
            )

        with col2:

            st.metric(
                "Type",
                rescue_team.get(
                    "team_type",
                    "N/A"
                )
            )

        with col3:

            distance = rescue_team.get(
                "distance_km"
            )

            st.metric(
                "Distance",
                (
                    f"{distance:.2f} km"
                    if distance is not None
                    else "N/A"
                )
            )

    else:

        st.warning(
            "⚠️ No rescue team available."
        )


    # ========================================================
    # EMERGENCY ROUTE
    # ========================================================

    st.header(
        "🗺️ Emergency Route"
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


    # ========================================================
    # CURRENT WEATHER
    # ========================================================

    st.header(
        "🌦️ Current Weather"
    )

    if weather.get(
        "success",
        False
    ):

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            temperature = weather.get(
                "temperature"
            )

            st.metric(
                "Temperature",
                (
                    f"{temperature:.2f} °C"
                    if temperature is not None
                    else "N/A"
                )
            )

        with col2:

            humidity = weather.get(
                "humidity"
            )

            st.metric(
                "Humidity",
                (
                    f"{humidity}%"
                    if humidity is not None
                    else "N/A"
                )
            )

        with col3:

            st.write(
                "**Weather:**",
                weather.get(
                    "weather",
                    "N/A"
                )
            )

        with col4:

            wind_speed = weather.get(
                "wind_speed"
            )

            st.metric(
                "Wind Speed",
                (
                    f"{wind_speed:.2f} m/s"
                    if wind_speed is not None
                    else "N/A"
                )
            )

    else:

        st.warning(
            f'⚠️ Weather unavailable: '
            f'{weather.get("error", "Unknown error")}'
        )


    # ========================================================
    # AI RECOMMENDATION
    # ========================================================

    st.header(
        "🤖 AI Emergency Recommendation"
    )

    recommendation = result.get(
        "gemini_recommendation",
        "No AI recommendation available."
    )

    st.markdown(
        recommendation
    )


    # ========================================================
    # EMERGENCY NOTIFICATION
    # ========================================================

    st.header(
        "🚨 Emergency Notification"
    )

    notification = result.get(
        "notification",
        "No emergency notification available."
    )

    st.code(
        notification,
        language="text"
    )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    st.divider()

    st.success(
        "✅ Emergency coordination completed successfully."
    )


# ============================================================
# INITIAL STATE
# ============================================================

else:

    st.info(
        "Click **🚨 Run Emergency Coordination** "
        "to start the emergency response workflow."
    )