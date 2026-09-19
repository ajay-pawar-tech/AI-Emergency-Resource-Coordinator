import streamlit as st

from app.database.db import SessionLocal
from app.database.models import Ambulance, RescueTeam


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Emergency Resources",
    page_icon="🚑",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🚑 Emergency Resource Management")

st.caption(
    "Add, view, update and delete ambulances and rescue teams using SQLite."
)


# ============================================================
# CONSTANTS
# ============================================================

AMBULANCE_STATUSES = [
    "available",
    "busy",
    "maintenance",
    "offline"
]

RESCUE_TEAM_STATUSES = [
    "available",
    "busy",
    "maintenance",
    "offline"
]

AMBULANCE_TYPES = [
    "Basic Life Support",
    "Advanced Life Support",
    "ICU Ambulance",
    "Neonatal Ambulance",
    "Other"
]

RESCUE_TEAM_TYPES = [
    "Flood Rescue",
    "Fire Rescue",
    "Mountain Rescue",
    "Urban Search and Rescue",
    "Medical Rescue",
    "Disaster Response",
    "Other"
]


# ============================================================
# DATABASE HELPERS
# ============================================================

def load_ambulances():
    """Load all ambulances from the database."""

    db = SessionLocal()

    try:
        return (
            db.query(Ambulance)
            .order_by(Ambulance.id.desc())
            .all()
        )

    finally:
        db.close()


def load_rescue_teams():
    """Load all rescue teams from the database."""

    db = SessionLocal()

    try:
        return (
            db.query(RescueTeam)
            .order_by(RescueTeam.id.desc())
            .all()
        )

    finally:
        db.close()


# ============================================================
# ADD RESOURCE TABS
# ============================================================

tab1, tab2 = st.tabs(
    [
        "🚑 Add Ambulance",
        "🚒 Add Rescue Team"
    ]
)


# ============================================================
# ADD AMBULANCE
# ============================================================

with tab1:

    st.header("➕ Add New Ambulance")

    with st.form("ambulance_form"):

        col1, col2 = st.columns(2)

        with col1:

            vehicle_number = st.text_input(
                "Vehicle Number",
                placeholder="Example: AMB-1042"
            )

            vehicle_type = st.selectbox(
                "Ambulance Type",
                AMBULANCE_TYPES
            )

        with col2:

            city = st.text_input(
                "City",
                value="Hyderabad"
            )

            status = st.selectbox(
                "Status",
                AMBULANCE_STATUSES
            )

        st.subheader("📍 Ambulance Location")

        col1, col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=17.3850,
                format="%.6f"
            )

        with col2:

            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=78.4867,
                format="%.6f"
            )

        capacity = st.number_input(
            "Patient Capacity",
            min_value=1,
            max_value=100,
            value=4,
            step=1
        )

        submit_ambulance = st.form_submit_button(
            "🚑 Save Ambulance",
            type="primary"
        )


# ============================================================
# SAVE AMBULANCE
# ============================================================

if submit_ambulance:

    if not vehicle_number.strip():

        st.error(
            "Please enter vehicle number."
        )

    elif not city.strip():

        st.error(
            "Please enter city."
        )

    else:

        db = SessionLocal()

        try:

            existing = (
                db.query(Ambulance)
                .filter(
                    Ambulance.vehicle_number
                    == vehicle_number.strip()
                )
                .first()
            )

            if existing:

                st.error(
                    "This ambulance already exists."
                )

            else:

                new_ambulance = Ambulance(
                    vehicle_number=vehicle_number.strip(),
                    vehicle_type=vehicle_type,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    city=city.strip(),
                    status=status,
                    capacity=int(capacity)
                )

                db.add(new_ambulance)

                db.commit()

                db.refresh(new_ambulance)

                st.success(
                    f"✅ Ambulance "
                    f"{new_ambulance.vehicle_number} "
                    "saved successfully."
                )

                st.rerun()

        except Exception as error:

            db.rollback()

            st.error(
                "❌ Failed to save ambulance."
            )

            st.exception(error)

        finally:

            db.close()


# ============================================================
# ADD RESCUE TEAM
# ============================================================

with tab2:

    st.header("➕ Add New Rescue Team")

    with st.form("rescue_team_form"):

        col1, col2 = st.columns(2)

        with col1:

            team_name = st.text_input(
                "Team Name",
                placeholder="Example: Rescue Team 27"
            )

            team_type = st.selectbox(
                "Rescue Team Type",
                RESCUE_TEAM_TYPES
            )

        with col2:

            city = st.text_input(
                "Team City",
                value="Hyderabad"
            )

            status = st.selectbox(
                "Team Status",
                RESCUE_TEAM_STATUSES
            )

        st.subheader("📍 Rescue Team Location")

        col1, col2 = st.columns(2)

        with col1:

            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=17.3850,
                format="%.6f"
            )

        with col2:

            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=78.4867,
                format="%.6f"
            )

        members = st.number_input(
            "Team Members",
            min_value=1,
            max_value=500,
            value=10,
            step=1
        )

        submit_team = st.form_submit_button(
            "🚒 Save Rescue Team",
            type="primary"
        )


# ============================================================
# SAVE RESCUE TEAM
# ============================================================

if submit_team:

    if not team_name.strip():

        st.error(
            "Please enter team name."
        )

    elif not city.strip():

        st.error(
            "Please enter team city."
        )

    else:

        db = SessionLocal()

        try:

            existing = (
                db.query(RescueTeam)
                .filter(
                    RescueTeam.team_name
                    == team_name.strip()
                )
                .first()
            )

            if existing:

                st.error(
                    "This rescue team already exists."
                )

            else:

                new_team = RescueTeam(
                    team_name=team_name.strip(),
                    team_type=team_type,
                    members=int(members),
                    latitude=float(latitude),
                    longitude=float(longitude),
                    city=city.strip(),
                    status=status
                )

                db.add(new_team)

                db.commit()

                db.refresh(new_team)

                st.success(
                    f"✅ Rescue team "
                    f"{new_team.team_name} "
                    "saved successfully."
                )

                st.rerun()

        except Exception as error:

            db.rollback()

            st.error(
                "❌ Failed to save rescue team."
            )

            st.exception(error)

        finally:

            db.close()


# ============================================================
# LOAD DATABASE DATA
# ============================================================

ambulances = load_ambulances()

rescue_teams = load_rescue_teams()


# ============================================================
# RESOURCE SUMMARY
# ============================================================

st.divider()

st.header("📊 Resource Summary")


available_ambulances = sum(
    1
    for ambulance in ambulances
    if ambulance.status.lower() == "available"
)


available_rescue_teams = sum(
    1
    for team in rescue_teams
    if team.status.lower() == "available"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🚑 Total Ambulances",
        len(ambulances)
    )


with col2:

    st.metric(
        "🟢 Available Ambulances",
        available_ambulances
    )


with col3:

    st.metric(
        "🚒 Total Rescue Teams",
        len(rescue_teams)
    )


with col4:

    st.metric(
        "🟢 Available Rescue Teams",
        available_rescue_teams
    )


# ============================================================
# AMBULANCE LIST
# ============================================================

st.divider()

st.header("🚑 Ambulance List")


if ambulances:

    ambulance_data = []

    for ambulance in ambulances:

        ambulance_data.append(
            {
                "ID": ambulance.id,
                "Vehicle": ambulance.vehicle_number,
                "Type": ambulance.vehicle_type,
                "City": ambulance.city,
                "Status": ambulance.status,
                "Capacity": ambulance.capacity,
                "Latitude": ambulance.latitude,
                "Longitude": ambulance.longitude
            }
        )

    st.dataframe(
        ambulance_data,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No ambulances are stored in the database."
    )


# ============================================================
# AMBULANCE MANAGEMENT
# ============================================================

if ambulances:

    st.subheader("🛠️ Ambulance Management")

    ambulance_ids = [
        ambulance.id
        for ambulance in ambulances
    ]

    selected_ambulance_id = st.selectbox(
        "Select Ambulance",
        ambulance_ids
    )

    selected_ambulance = next(
        (
            ambulance
            for ambulance in ambulances
            if ambulance.id == selected_ambulance_id
        ),
        None
    )


    if selected_ambulance:

        # ====================================================
        # UPDATE AMBULANCE
        # ====================================================

        with st.form(
            f"update_ambulance_{selected_ambulance.id}"
        ):

            st.write(
                f"### ✏️ Update Ambulance "
                f"#{selected_ambulance.id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                update_vehicle = st.text_input(
                    "Vehicle Number",
                    value=selected_ambulance.vehicle_number
                )

                update_type = st.selectbox(
                    "Ambulance Type",
                    AMBULANCE_TYPES,
                    index=(
                        AMBULANCE_TYPES.index(
                            selected_ambulance.vehicle_type
                        )
                        if selected_ambulance.vehicle_type
                        in AMBULANCE_TYPES
                        else len(AMBULANCE_TYPES) - 1
                    )
                )

                update_city = st.text_input(
                    "City",
                    value=selected_ambulance.city
                )

            with col2:

                update_status = st.selectbox(
                    "Status",
                    AMBULANCE_STATUSES,
                    index=(
                        AMBULANCE_STATUSES.index(
                            selected_ambulance.status.lower()
                        )
                        if selected_ambulance.status.lower()
                        in AMBULANCE_STATUSES
                        else 0
                    )
                )

                update_capacity = st.number_input(
                    "Patient Capacity",
                    min_value=1,
                    max_value=100,
                    value=int(
                        selected_ambulance.capacity or 1
                    ),
                    step=1
                )


            col1, col2 = st.columns(2)

            with col1:

                update_latitude = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=float(
                        selected_ambulance.latitude
                        or 17.3850
                    ),
                    format="%.6f"
                )

            with col2:

                update_longitude = st.number_input(
                    "Longitude",
                    min_value=-180.0,
                    max_value=180.0,
                    value=float(
                        selected_ambulance.longitude
                        or 78.4867
                    ),
                    format="%.6f"
                )

            update_ambulance_button = (
                st.form_submit_button(
                    "💾 Update Ambulance",
                    type="primary"
                )
            )


        # ====================================================
        # SAVE AMBULANCE UPDATE
        # ====================================================

        if update_ambulance_button:

            if not update_vehicle.strip():

                st.error(
                    "Vehicle number cannot be empty."
                )

            elif not update_city.strip():

                st.error(
                    "City cannot be empty."
                )

            else:

                db = SessionLocal()

                try:

                    ambulance = (
                        db.query(Ambulance)
                        .filter(
                            Ambulance.id
                            == selected_ambulance.id
                        )
                        .first()
                    )

                    if ambulance:

                        duplicate = (
                            db.query(Ambulance)
                            .filter(
                                Ambulance.vehicle_number
                                == update_vehicle.strip(),
                                Ambulance.id
                                != selected_ambulance.id
                            )
                            .first()
                        )

                        if duplicate:

                            st.error(
                                "Another ambulance already "
                                "uses this vehicle number."
                            )

                        else:

                            ambulance.vehicle_number = (
                                update_vehicle.strip()
                            )

                            ambulance.vehicle_type = (
                                update_type
                            )

                            ambulance.city = (
                                update_city.strip()
                            )

                            ambulance.status = (
                                update_status
                            )

                            ambulance.capacity = (
                                int(update_capacity)
                            )

                            ambulance.latitude = (
                                float(update_latitude)
                            )

                            ambulance.longitude = (
                                float(update_longitude)
                            )

                            db.commit()

                            st.success(
                                f"✅ Ambulance "
                                f"#{ambulance.id} "
                                "updated successfully."
                            )

                            st.rerun()

                except Exception as error:

                    db.rollback()

                    st.error(
                        "❌ Failed to update ambulance."
                    )

                    st.exception(error)

                finally:

                    db.close()


        # ====================================================
        # DELETE AMBULANCE
        # ====================================================

        st.subheader(
            f"🗑️ Delete Ambulance "
            f"#{selected_ambulance.id}"
        )

        confirm_ambulance_delete = st.checkbox(
            "I confirm permanent deletion of this ambulance."
        )

        if st.button(
            "🗑️ Delete Selected Ambulance",
            disabled=not confirm_ambulance_delete
        ):

            db = SessionLocal()

            try:

                ambulance = (
                    db.query(Ambulance)
                    .filter(
                        Ambulance.id
                        == selected_ambulance.id
                    )
                    .first()
                )

                if ambulance:

                    db.delete(
                        ambulance
                    )

                    db.commit()

                    st.success(
                        "✅ Ambulance deleted successfully."
                    )

                    st.rerun()

            except Exception as error:

                db.rollback()

                st.error(
                    "❌ Failed to delete ambulance."
                )

                st.exception(error)

            finally:

                db.close()


# ============================================================
# RESCUE TEAM LIST
# ============================================================

st.divider()

st.header("🚒 Rescue Team List")


if rescue_teams:

    rescue_data = []

    for team in rescue_teams:

        rescue_data.append(
            {
                "ID": team.id,
                "Team": team.team_name,
                "Type": team.team_type,
                "Members": team.members,
                "City": team.city,
                "Status": team.status,
                "Latitude": team.latitude,
                "Longitude": team.longitude
            }
        )

    st.dataframe(
        rescue_data,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No rescue teams are stored in the database."
    )


# ============================================================
# RESCUE TEAM MANAGEMENT
# ============================================================

if rescue_teams:

    st.subheader("🛠️ Rescue Team Management")

    rescue_team_ids = [
        team.id
        for team in rescue_teams
    ]

    selected_team_id = st.selectbox(
        "Select Rescue Team",
        rescue_team_ids
    )

    selected_team = next(
        (
            team
            for team in rescue_teams
            if team.id == selected_team_id
        ),
        None
    )


    if selected_team:

        # ====================================================
        # UPDATE RESCUE TEAM
        # ====================================================

        with st.form(
            f"update_team_{selected_team.id}"
        ):

            st.write(
                f"### ✏️ Update Rescue Team "
                f"#{selected_team.id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                update_team_name = st.text_input(
                    "Team Name",
                    value=selected_team.team_name
                )

                update_team_type = st.selectbox(
                    "Rescue Team Type",
                    RESCUE_TEAM_TYPES,
                    index=(
                        RESCUE_TEAM_TYPES.index(
                            selected_team.team_type
                        )
                        if selected_team.team_type
                        in RESCUE_TEAM_TYPES
                        else len(RESCUE_TEAM_TYPES) - 1
                    )
                )

                update_team_city = st.text_input(
                    "Team City",
                    value=selected_team.city
                )

            with col2:

                update_team_status = st.selectbox(
                    "Status",
                    RESCUE_TEAM_STATUSES,
                    index=(
                        RESCUE_TEAM_STATUSES.index(
                            selected_team.status.lower()
                        )
                        if selected_team.status.lower()
                        in RESCUE_TEAM_STATUSES
                        else 0
                    )
                )

                update_members = st.number_input(
                    "Team Members",
                    min_value=1,
                    max_value=500,
                    value=int(
                        selected_team.members or 1
                    ),
                    step=1
                )


            col1, col2 = st.columns(2)

            with col1:

                update_team_latitude = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=float(
                        selected_team.latitude
                        or 17.3850
                    ),
                    format="%.6f"
                )

            with col2:

                update_team_longitude = st.number_input(
                    "Longitude",
                    min_value=-180.0,
                    max_value=180.0,
                    value=float(
                        selected_team.longitude
                        or 78.4867
                    ),
                    format="%.6f"
                )


            update_team_button = st.form_submit_button(
                "💾 Update Rescue Team",
                type="primary"
            )


        # ====================================================
        # SAVE TEAM UPDATE
        # ====================================================

        if update_team_button:

            if not update_team_name.strip():

                st.error(
                    "Team name cannot be empty."
                )

            elif not update_team_city.strip():

                st.error(
                    "Team city cannot be empty."
                )

            else:

                db = SessionLocal()

                try:

                    team = (
                        db.query(RescueTeam)
                        .filter(
                            RescueTeam.id
                            == selected_team.id
                        )
                        .first()
                    )


                    if team:

                        duplicate = (
                            db.query(RescueTeam)
                            .filter(
                                RescueTeam.team_name
                                == update_team_name.strip(),
                                RescueTeam.id
                                != selected_team.id
                            )
                            .first()
                        )


                        if duplicate:

                            st.error(
                                "Another rescue team already "
                                "uses this name."
                            )

                        else:

                            team.team_name = (
                                update_team_name.strip()
                            )

                            team.team_type = (
                                update_team_type
                            )

                            team.city = (
                                update_team_city.strip()
                            )

                            team.status = (
                                update_team_status
                            )

                            team.members = (
                                int(update_members)
                            )

                            team.latitude = (
                                float(
                                    update_team_latitude
                                )
                            )

                            team.longitude = (
                                float(
                                    update_team_longitude
                                )
                            )

                            db.commit()

                            st.success(
                                f"✅ Rescue Team "
                                f"#{team.id} "
                                "updated successfully."
                            )

                            st.rerun()

                except Exception as error:

                    db.rollback()

                    st.error(
                        "❌ Failed to update rescue team."
                    )

                    st.exception(error)

                finally:

                    db.close()


        # ====================================================
        # DELETE RESCUE TEAM
        # ====================================================

        st.subheader(
            f"🗑️ Delete Rescue Team "
            f"#{selected_team.id}"
        )

        confirm_team_delete = st.checkbox(
            "I confirm permanent deletion of this rescue team."
        )


        if st.button(
            "🗑️ Delete Selected Rescue Team",
            disabled=not confirm_team_delete
        ):

            db = SessionLocal()

            try:

                team = (
                    db.query(RescueTeam)
                    .filter(
                        RescueTeam.id
                        == selected_team.id
                    )
                    .first()
                )


                if team:

                    db.delete(
                        team
                    )

                    db.commit()

                    st.success(
                        "✅ Rescue team deleted successfully."
                    )

                    st.rerun()


            except Exception as error:

                db.rollback()

                st.error(
                    "❌ Failed to delete rescue team."
                )

                st.exception(error)

            finally:

                db.close()