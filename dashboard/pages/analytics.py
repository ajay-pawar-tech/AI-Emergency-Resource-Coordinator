import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

# Get project root.
BASE_DIR = Path(__file__).resolve().parents[2]

# Add project root to Python path.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# Dashboard directory.
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Add dashboard directory to Python path.
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


# ============================================================
# IMPORTS
# ============================================================

from app.agents.coordinator_agent import coordinate_emergency
from components.charts import display_emergency_charts


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Emergency Analytics",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📊 Emergency Analytics")

st.caption(
    "Emergency demand, incidents, victims and resource analytics"
)


# ============================================================
# RUN ANALYTICS
# ============================================================

if st.button(
    "📊 Generate Emergency Analytics",
    type="primary"
):

    with st.spinner(
        "Generating emergency analytics..."
    ):

        try:

            result = coordinate_emergency()

        except Exception as error:

            st.error(
                "Failed to generate analytics."
            )

            st.exception(error)

            st.stop()


    st.success(
        "Emergency analytics generated successfully."
    )


    # ========================================================
    # KPI SUMMARY
    # ========================================================

    incident_summary = result.get(
        "incident_summary",
        {}
    )

    victim_summary = result.get(
        "victim_summary",
        {}
    )

    hospital_summary = result.get(
        "hospital_summary",
        {}
    )

    resource_summary = result.get(
        "resource_summary",
        {}
    )

    demand_forecast = result.get(
        "demand_forecast",
        0
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.header("📈 Emergency KPI Summary")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Predicted Demand",
            f"{float(demand_forecast):.3f}"
        )


    with col2:

        st.metric(
            "Total Incidents",
            incident_summary.get(
                "total_incidents",
                0
            )
        )


    with col3:

        st.metric(
            "Total Victims",
            victim_summary.get(
                "total_victims",
                0
            )
        )


    with col4:

        st.metric(
            "Available Ambulances",
            resource_summary.get(
                "available_ambulances",
                0
            )
        )


    # ========================================================
    # SECOND KPI ROW
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Active Hospitals",
            hospital_summary.get(
                "active_hospitals",
                0
            )
        )


    with col2:

        st.metric(
            "Available Beds",
            hospital_summary.get(
                "available_beds",
                0
            )
        )


    with col3:

        st.metric(
            "Rescue Teams",
            resource_summary.get(
                "available_rescue_teams",
                0
            )
        )


    with col4:

        st.metric(
            "Hospital Capacity",
            hospital_summary.get(
                "available_beds",
                0
            )
        )


    # ========================================================
    # CHARTS
    # ========================================================

    st.divider()

    try:

        display_emergency_charts(
            result
        )

    except Exception as error:

        st.warning(
            "Unable to display emergency charts."
        )

        st.exception(error)


    # ========================================================
    # ANALYTICS SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "🧠 AI Analytics Summary"
    )


    # Determine demand level.
    if demand_forecast >= 0.8:

        demand_status = "High"

    elif demand_forecast >= 0.5:

        demand_status = "Medium"

    else:

        demand_status = "Low"


    st.write(
        f"**Emergency Demand Level:** {demand_status}"
    )


    st.write(
        f"**Predicted Demand:** "
        f"{float(demand_forecast):.3f}"
    )


    st.write(
        f"**Total Incidents:** "
        f"{incident_summary.get('total_incidents', 0)}"
    )


    st.write(
        f"**Total Victims:** "
        f"{victim_summary.get('total_victims', 0)}"
    )


    st.write(
        f"**Available Ambulances:** "
        f"{resource_summary.get('available_ambulances', 0)}"
    )


    st.write(
        f"**Available Hospital Beds:** "
        f"{hospital_summary.get('available_beds', 0)}"
    )


    st.write(
        f"**Available Rescue Teams:** "
        f"{resource_summary.get('available_rescue_teams', 0)}"
    )


else:

    st.info(
        "Click **📊 Generate Emergency Analytics** "
        "to generate the latest emergency analytics."
    )