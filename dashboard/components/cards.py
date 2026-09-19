import streamlit as st


def display_emergency_cards(result):
    """
    Display emergency statistics as KPI cards.
    """

    # ==========================================================
    # EXTRACT DATA
    # ==========================================================

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


    # ==========================================================
    # FIRST ROW
    # ==========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            label="📈 Predicted Demand",
            value=f"{demand_forecast:.3f}"
        )

    with col2:

        st.metric(
            label="🚨 Total Incidents",
            value=incident_summary.get(
                "total_incidents",
                0
            )
        )

    with col3:

        st.metric(
            label="👥 Total Victims",
            value=victim_summary.get(
                "total_victims",
                0
            )
        )

    with col4:

        st.metric(
            label="🚑 Available Ambulances",
            value=resource_summary.get(
                "available_ambulances",
                0
            )
        )


    # ==========================================================
    # SECOND ROW
    # ==========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            label="🏥 Active Hospitals",
            value=hospital_summary.get(
                "active_hospitals",
                0
            )
        )

    with col2:

        st.metric(
            label="🛏️ Available Beds",
            value=hospital_summary.get(
                "available_beds",
                0
            )
        )

    with col3:

        st.metric(
            label="🚒 Rescue Teams",
            value=resource_summary.get(
                "available_rescue_teams",
                0
            )
        )

    with col4:

        hospitals_with_beds = hospital_summary.get(
            "hospitals_with_2_beds",
            "N/A"
        )

        st.metric(
            label="🏥 Hospitals with Beds",
            value=hospitals_with_beds
        )