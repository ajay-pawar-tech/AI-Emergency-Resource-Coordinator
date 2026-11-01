import streamlit as st
import pandas as pd


def display_emergency_charts(result):
    """
    Display emergency resource and hospital analytics charts.
    """

    # ==========================================================
    # EXTRACT DATA
    # ==========================================================

    incident_summary = result.get("incident_summary", {})
    victim_summary = result.get("victim_summary", {})
    hospital_summary = result.get("hospital_summary", {})
    resource_summary = result.get("resource_summary", {})
    demand_forecast = result.get("demand_forecast", 0)


    # ==========================================================
    # SECTION TITLE
    # ==========================================================

    st.subheader("📊 Emergency Analytics")


    # ==========================================================
    # RESOURCE AVAILABILITY CHART
    # ==========================================================

    st.markdown("### 🚑 Emergency Resource Availability")

    resource_data = pd.DataFrame(
        {
            "Resource": [
                "Ambulances",
                "Rescue Teams",
                "Hospitals"
            ],
            "Available": [
                resource_summary.get("available_ambulances", 0),
                resource_summary.get("available_rescue_teams", 0),
                hospital_summary.get("active_hospitals", 0)
            ]
        }
    )

    st.bar_chart(
        resource_data.set_index("Resource")
    )


        # ==========================================================
    # HOSPITAL CAPACITY
    # ==========================================================

    st.markdown("### 🏥 Hospital Capacity")

    total_beds = hospital_summary.get("total_beds", 0)
    available_beds = hospital_summary.get("available_beds", 0)

    occupied_beds = max(
        0,
        total_beds - available_beds
    )

    utilization_percentage = (
        (occupied_beds / total_beds) * 100
        if total_beds > 0
        else 0
    )

    hospital_data = pd.DataFrame(
        {
            "Category": [
                "Available Beds",
                "Occupied Beds"
            ],
            "Count": [
                available_beds,
                occupied_beds
            ]
        }
    )

    st.bar_chart(
        hospital_data.set_index("Category")
    )

    st.caption(
        f"Bed Utilization: {utilization_percentage:.1f}% "
        f"| Available: {available_beds:,} "
        f"| Occupied: {occupied_beds:,} "
        f"| Total: {total_beds:,}"
    )


    # ==========================================================
    # INCIDENT & VICTIM OVERVIEW
    # ==========================================================

    st.markdown("### 🚨 Incident & Victim Overview")

    incident_data = pd.DataFrame(
        {
            "Category": [
                "Incidents",
                "Victims"
            ],
            "Count": [
                incident_summary.get("total_incidents", 0),
                victim_summary.get("total_victims", 0)
            ]
        }
    )

    st.bar_chart(
        incident_data.set_index("Category")
    )


    # ==========================================================
    # DEMAND FORECAST
    # ==========================================================

    st.markdown("### 📈 Emergency Demand Forecast")

    demand_data = pd.DataFrame(
        {
            "Metric": [
                "Predicted Demand"
            ],
            "Value": [
                float(demand_forecast)
            ]
        }
    )

    st.bar_chart(
        demand_data.set_index("Metric")
    )