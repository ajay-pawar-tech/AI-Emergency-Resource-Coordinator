import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = BASE_DIR / "dashboard"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))


# ============================================================
# DATABASE IMPORTS
# ============================================================

from app.database.db import SessionLocal
from app.database.models import Incident


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Incident Management",
    page_icon="🚨",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_all_incidents():
    """
    Return all incidents ordered by newest first.
    """

    db = SessionLocal()

    try:
        return (
            db.query(Incident)
            .order_by(
                Incident.created_at.desc(),
                Incident.id.desc(),
            )
            .all()
        )

    finally:
        db.close()


def get_incident_by_id(incident_id):
    """
    Return one incident by ID.
    """

    db = SessionLocal()

    try:
        return (
            db.query(Incident)
            .filter(
                Incident.id == incident_id
            )
            .first()
        )

    finally:
        db.close()


def add_incident(
    incident_type,
    severity,
    city,
    location,
    latitude,
    longitude,
    victims,
    critical_victims,
    description,
    status,
):
    """
    Add a new operational incident.
    """

    db = SessionLocal()

    try:

        new_incident = Incident(
            incident_type=incident_type,
            severity=severity,
            city=city,
            location=location,
            latitude=latitude,
            longitude=longitude,
            victims=victims,
            critical_victims=critical_victims,
            description=description,
            status=status,
        )

        db.add(
            new_incident
        )

        db.commit()

        db.refresh(
            new_incident
        )

        return new_incident.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def update_incident(
    incident_id,
    incident_type,
    severity,
    city,
    location,
    latitude,
    longitude,
    victims,
    critical_victims,
    description,
    status,
):
    """
    Update an existing incident.
    """

    db = SessionLocal()

    try:

        incident = (
            db.query(Incident)
            .filter(
                Incident.id == incident_id
            )
            .first()
        )

        if incident is None:
            return False

        incident.incident_type = incident_type
        incident.severity = severity
        incident.city = city
        incident.location = location
        incident.latitude = latitude
        incident.longitude = longitude
        incident.victims = victims
        incident.critical_victims = critical_victims
        incident.description = description
        incident.status = status

        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def delete_incident(
    incident_id
):
    """
    Delete an incident by ID.
    """

    db = SessionLocal()

    try:

        incident = (
            db.query(Incident)
            .filter(
                Incident.id == incident_id
            )
            .first()
        )

        if incident is None:
            return False

        db.delete(
            incident
        )

        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "🚨 Incident Management"
)

st.caption(
    "Manage emergency incidents stored in the SQLite database."
)


# ============================================================
# LOAD INCIDENTS
# ============================================================

incidents = get_all_incidents()


# ============================================================
# SUMMARY METRICS
# ============================================================

total_incidents = len(
    incidents
)

active_incidents = sum(
    1
    for incident in incidents
    if str(
        incident.status
    ).lower()
    in {
        "active",
        "in_progress",
    }
)

resolved_incidents = sum(
    1
    for incident in incidents
    if str(
        incident.status
    ).lower()
    == "resolved"
)

total_victims = sum(
    incident.victims or 0
    for incident in incidents
)

critical_victims = sum(
    incident.critical_victims or 0
    for incident in incidents
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:
    st.metric(
        "Total Incidents",
        total_incidents
    )


with col2:
    st.metric(
        "Active / In Progress",
        active_incidents
    )


with col3:
    st.metric(
        "Resolved",
        resolved_incidents
    )


with col4:
    st.metric(
        "Total Victims",
        total_victims
    )


with col5:
    st.metric(
        "Critical Victims",
        critical_victims
    )


st.divider()


# ============================================================
# ADD INCIDENT
# ============================================================

st.header(
    "➕ Add New Incident"
)

with st.form(
    "add_incident_form",
    clear_on_submit=True,
):

    col1, col2, col3 = st.columns(3)

    with col1:

        incident_type = st.selectbox(
            "Incident Type",
            [
                "Road Accident",
                "Fire",
                "Industrial Accident",
                "Building Collapse",
                "Medical Emergency",
                "Flood",
                "Other",
            ],
        )

    with col2:

        severity = st.selectbox(
            "Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical",
            ],
        )

    with col3:

        status = st.selectbox(
            "Status",
            [
                "Active",
                "In_Progress",
                "Resolved",
                "Cancelled",
            ],
        )

    col1, col2 = st.columns(2)

    with col1:

        city = st.text_input(
            "City",
            value="Hyderabad",
        )

    with col2:

        location = st.text_input(
            "Location",
            placeholder="e.g. Ameerpeth",
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        latitude = st.number_input(
            "Latitude",
            value=17.385044,
            format="%.6f",
        )

    with col2:

        longitude = st.number_input(
            "Longitude",
            value=78.486671,
            format="%.6f",
        )

    with col3:

        victims = st.number_input(
            "Total Victims",
            min_value=0,
            value=1,
            step=1,
        )

    with col4:

        critical_victims = st.number_input(
            "Critical Victims",
            min_value=0,
            value=0,
            step=1,
        )

    description = st.text_area(
        "Description",
        placeholder="Describe the emergency situation...",
    )

    add_button = st.form_submit_button(
        "🚨 Add Incident",
        type="primary",
    )


if add_button:

    if not location.strip():

        st.error(
            "Please enter an incident location."
        )

    elif critical_victims > victims:

        st.error(
            "Critical victims cannot exceed total victims."
        )

    else:

        try:

            incident_id = add_incident(
                incident_type=incident_type,
                severity=severity,
                city=city.strip(),
                location=location.strip(),
                latitude=float(latitude),
                longitude=float(longitude),
                victims=int(victims),
                critical_victims=int(
                    critical_victims
                ),
                description=description.strip(),
                status=status,
            )

            st.success(
                f"✅ Incident #{incident_id} added successfully."
            )

            st.rerun()

        except Exception as error:

            st.error(
                "❌ Failed to add incident."
            )

            st.exception(error)


# ============================================================
# SEARCH AND FILTER
# ============================================================

st.divider()

st.header(
    "📋 Incident Records"
)


col1, col2, col3 = st.columns(3)


with col1:

    search_text = st.text_input(
        "🔍 Search",
        placeholder="Type, city or location...",
    )


with col2:

    status_filter = st.selectbox(
        "Filter by Status",
        [
            "All",
            "Active",
            "In_Progress",
            "Resolved",
            "Cancelled",
        ],
    )


with col3:

    severity_filter = st.selectbox(
        "Filter by Severity",
        [
            "All",
            "Low",
            "Medium",
            "High",
            "Critical",
        ],
    )


# ============================================================
# FILTER DATA
# ============================================================

filtered_incidents = []

search_text_lower = (
    search_text.strip().lower()
)


for incident in incidents:

    incident_status = str(
        incident.status or ""
    )

    incident_severity = str(
        incident.severity or ""
    )

    searchable_text = " ".join(
        [
            str(
                incident.incident_type
                or ""
            ),
            str(
                incident.city
                or ""
            ),
            str(
                incident.location
                or ""
            ),
        ]
    ).lower()

    if search_text_lower:

        if search_text_lower not in searchable_text:

            continue

    if status_filter != "All":

        if incident_status.lower() != (
            status_filter.lower()
        ):

            continue

    if severity_filter != "All":

        if incident_severity.lower() != (
            severity_filter.lower()
        ):

            continue

    filtered_incidents.append(
        incident
    )


# ============================================================
# DISPLAY TABLE
# ============================================================

if not filtered_incidents:

    st.info(
        "No incidents match the selected filters."
    )

else:

    table_rows = []

    for incident in filtered_incidents:

        table_rows.append(
            {
                "ID": incident.id,
                "Type": incident.incident_type,
                "Severity": incident.severity,
                "City": incident.city,
                "Location": incident.location,
                "Victims": incident.victims or 0,
                "Critical": (
                    incident.critical_victims or 0
                ),
                "Status": incident.status,
                "Created": (
                    incident.created_at.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    if incident.created_at
                    else "N/A"
                ),
            }
        )

    df = pd.DataFrame(
        table_rows
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# UPDATE INCIDENT
# ============================================================

st.divider()

st.header(
    "✏️ Update Incident"
)


if incidents:

    incident_options = {
        f"#{incident.id} | "
        f"{incident.incident_type} | "
        f"{incident.location} | "
        f"{incident.status}":
        incident.id
        for incident in incidents
    }

    selected_label = st.selectbox(
        "Select Incident",
        list(
            incident_options.keys()
        ),
    )

    selected_id = incident_options[
        selected_label
    ]

    selected_incident = get_incident_by_id(
        selected_id
    )

    if selected_incident:

        with st.form(
            "update_incident_form"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                update_type = st.text_input(
                    "Incident Type",
                    value=(
                        selected_incident.incident_type
                        or ""
                    ),
                )

            with col2:

                update_severity = st.selectbox(
                    "Severity",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ],
                    index=[
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ].index(
                        selected_incident.severity
                    )
                    if selected_incident.severity
                    in [
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ]
                    else 0,
                )

            with col3:

                status_options = [
                    "Active",
                    "In_Progress",
                    "Resolved",
                    "Cancelled",
                ]

                current_status = (
                    selected_incident.status
                    or "Active"
                )

                if current_status not in status_options:

                    current_status = "Active"

                update_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(
                        current_status
                    ),
                )

            col1, col2 = st.columns(2)

            with col1:

                update_city = st.text_input(
                    "City",
                    value=(
                        selected_incident.city
                        or ""
                    ),
                )

            with col2:

                update_location = st.text_input(
                    "Location",
                    value=(
                        selected_incident.location
                        or ""
                    ),
                )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                update_latitude = st.number_input(
                    "Latitude",
                    value=float(
                        selected_incident.latitude
                        or 0
                    ),
                    format="%.6f",
                )

            with col2:

                update_longitude = st.number_input(
                    "Longitude",
                    value=float(
                        selected_incident.longitude
                        or 0
                    ),
                    format="%.6f",
                )

            with col3:

                update_victims = st.number_input(
                    "Total Victims",
                    min_value=0,
                    value=int(
                        selected_incident.victims
                        or 0
                    ),
                    step=1,
                )

            with col4:

                update_critical = st.number_input(
                    "Critical Victims",
                    min_value=0,
                    value=int(
                        selected_incident.critical_victims
                        or 0
                    ),
                    step=1,
                )

            update_description = st.text_area(
                "Description",
                value=(
                    selected_incident.description
                    or ""
                ),
            )

            update_button = st.form_submit_button(
                "💾 Update Incident",
                type="primary",
            )


        if update_button:

            if (
                update_critical
                > update_victims
            ):

                st.error(
                    "Critical victims cannot exceed total victims."
                )

            else:

                try:

                    updated = update_incident(
                        incident_id=selected_id,
                        incident_type=update_type.strip(),
                        severity=update_severity,
                        city=update_city.strip(),
                        location=update_location.strip(),
                        latitude=float(
                            update_latitude
                        ),
                        longitude=float(
                            update_longitude
                        ),
                        victims=int(
                            update_victims
                        ),
                        critical_victims=int(
                            update_critical
                        ),
                        description=(
                            update_description.strip()
                        ),
                        status=update_status,
                    )

                    if updated:

                        st.success(
                            f"✅ Incident #{selected_id} updated successfully."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Incident not found."
                        )

                except Exception as error:

                    st.error(
                        "❌ Failed to update incident."
                    )

                    st.exception(error)


# ============================================================
# DELETE INCIDENT
# ============================================================

st.divider()

st.header(
    "🗑️ Delete Incident"
)


if incidents:

    delete_options = {
        f"#{incident.id} | "
        f"{incident.incident_type} | "
        f"{incident.location}":
        incident.id
        for incident in incidents
    }

    delete_label = st.selectbox(
        "Select Incident to Delete",
        list(
            delete_options.keys()
        ),
    )

    delete_id = delete_options[
        delete_label
    ]

    delete_target = get_incident_by_id(
        delete_id
    )

    if delete_target:

        is_historical = (
            delete_target.location
            == "Historical Incident"
        )

        if is_historical:

            st.warning(
                "⚠️ This is a historical imported incident. "
                "Deleting it will reduce your historical dataset."
            )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this incident."
        )

        if st.button(
            "🗑️ Delete Selected Incident",
            type="secondary",
        ):

            if not confirm_delete:

                st.error(
                    "Please confirm deletion first."
                )

            else:

                try:

                    deleted = delete_incident(
                        delete_id
                    )

                    if deleted:

                        st.success(
                            f"✅ Incident #{delete_id} deleted successfully."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Incident not found."
                        )

                except Exception as error:

                    st.error(
                        "❌ Failed to delete incident."
                    )

                    st.exception(error)


# ============================================================
# INCIDENT DETAILS
# ============================================================

st.divider()

st.header(
    "🔎 Incident Details"
)

if incidents:

    detail_options = {
        f"#{incident.id} | "
        f"{incident.incident_type} | "
        f"{incident.location}":
        incident.id
        for incident in incidents
    }

    detail_label = st.selectbox(
        "Select Incident",
        list(
            detail_options.keys()
        ),
        key="incident_details_selector",
    )

    detail_id = detail_options[
        detail_label
    ]

    detail_incident = get_incident_by_id(
        detail_id
    )

    if detail_incident:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                "**Incident ID:**",
                detail_incident.id
            )

            st.write(
                "**Incident Type:**",
                detail_incident.incident_type
            )

            st.write(
                "**Severity:**",
                detail_incident.severity
            )

            st.write(
                "**Status:**",
                detail_incident.status
            )

        with col2:

            st.write(
                "**City:**",
                detail_incident.city
            )

            st.write(
                "**Location:**",
                detail_incident.location
            )

            st.write(
                "**Victims:**",
                detail_incident.victims or 0
            )

            st.write(
                "**Critical Victims:**",
                detail_incident.critical_victims or 0
            )

        with col3:

            st.write(
                "**Latitude:**",
                detail_incident.latitude
            )

            st.write(
                "**Longitude:**",
                detail_incident.longitude
            )

            st.write(
                "**Created At:**",
                detail_incident.created_at
                if detail_incident.created_at
                else "N/A"
            )

        st.write(
            "**Description:**"
        )

        st.info(
            detail_incident.description
            or "No description available."
        )