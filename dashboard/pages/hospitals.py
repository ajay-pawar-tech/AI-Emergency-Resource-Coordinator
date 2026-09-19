import streamlit as st

from app.database.db import SessionLocal
from app.database.models import Hospital


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hospital Management",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🏥 Hospital Management")

st.caption(
    "Add, view, update and delete emergency hospitals using SQLite."
)


# ============================================================
# CONSTANTS
# ============================================================

HOSPITAL_STATUSES = [
    "active",
    "inactive",
    "emergency_only"
]


# ============================================================
# ADD NEW HOSPITAL
# ============================================================

st.header("➕ Add New Hospital")

with st.form("hospital_form"):

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------

    st.subheader("🏥 Hospital Information")

    col1, col2 = st.columns(2)

    with col1:

        hospital_name = st.text_input(
            "Hospital Name",
            placeholder="Example: Apollo Hospital"
        )

    with col2:

        city = st.text_input(
            "City",
            value="Hyderabad"
        )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    st.subheader("📍 Hospital Location")

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


    # --------------------------------------------------------
    # BED INFORMATION
    # --------------------------------------------------------

    st.subheader("🛏️ Bed Information")

    col1, col2 = st.columns(2)

    with col1:

        total_beds = st.number_input(
            "Total Beds",
            min_value=1,
            max_value=100000,
            value=100,
            step=1
        )

    with col2:

        available_beds = st.number_input(
            "Available Beds",
            min_value=0,
            max_value=100000,
            value=50,
            step=1
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = st.selectbox(
        "Hospital Status",
        HOSPITAL_STATUSES
    )


    # --------------------------------------------------------
    # SAVE BUTTON
    # --------------------------------------------------------

    submitted = st.form_submit_button(
        "🏥 Save Hospital",
        type="primary"
    )


# ============================================================
# SAVE HOSPITAL
# ============================================================

if submitted:

    if not hospital_name.strip():

        st.error(
            "Please enter hospital name."
        )

    elif not city.strip():

        st.error(
            "Please enter city."
        )

    elif available_beds > total_beds:

        st.error(
            "Available beds cannot exceed total beds."
        )

    else:

        db = SessionLocal()

        try:

            # Check duplicate hospital name.
            existing = (
                db.query(Hospital)
                .filter(
                    Hospital.name
                    == hospital_name.strip()
                )
                .first()
            )


            if existing:

                st.error(
                    "A hospital with this name already exists."
                )

            else:

                new_hospital = Hospital(

                    name=hospital_name.strip(),

                    city=city.strip(),

                    latitude=float(
                        latitude
                    ),

                    longitude=float(
                        longitude
                    ),

                    total_beds=int(
                        total_beds
                    ),

                    available_beds=int(
                        available_beds
                    ),

                    status=status
                )


                db.add(
                    new_hospital
                )

                db.commit()

                db.refresh(
                    new_hospital
                )


                st.success(
                    f"✅ Hospital #{new_hospital.id} "
                    "saved successfully."
                )


                st.rerun()


        except Exception as error:

            db.rollback()

            st.error(
                "❌ Failed to save hospital."
            )

            st.exception(
                error
            )

        finally:

            db.close()


# ============================================================
# LOAD HOSPITALS
# ============================================================

db = SessionLocal()

try:

    hospitals = (
        db.query(Hospital)
        .order_by(
            Hospital.id.desc()
        )
        .all()
    )

except Exception as error:

    hospitals = []

    st.error(
        "❌ Failed to load hospitals."
    )

    st.exception(
        error
    )

finally:

    db.close()


# ============================================================
# HOSPITAL SUMMARY
# ============================================================

st.divider()

st.header("📊 Hospital Summary")


if hospitals:

    total_hospitals = len(
        hospitals
    )


    active_hospitals = sum(
        1
        for hospital in hospitals
        if hospital.status == "active"
    )


    total_beds_all = sum(
        hospital.total_beds or 0
        for hospital in hospitals
    )


    available_beds_all = sum(
        hospital.available_beds or 0
        for hospital in hospitals
    )


    hospitals_with_beds = sum(
        1
        for hospital in hospitals
        if (hospital.available_beds or 0) > 0
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            "🏥 Total Hospitals",
            total_hospitals
        )


    with col2:

        st.metric(
            "🟢 Active Hospitals",
            active_hospitals
        )


    with col3:

        st.metric(
            "🛏️ Total Beds",
            total_beds_all
        )


    with col4:

        st.metric(
            "🛏️ Available Beds",
            available_beds_all
        )


    with col5:

        st.metric(
            "✅ Hospitals with Beds",
            hospitals_with_beds
        )


    # ========================================================
    # HOSPITAL TABLE
    # ========================================================

    st.header("📋 Hospital Records")


    hospital_data = []


    for hospital in hospitals:

        hospital_data.append(
            {
                "ID":
                    hospital.id,

                "Hospital":
                    hospital.name,

                "City":
                    hospital.city,

                "Total Beds":
                    hospital.total_beds,

                "Available Beds":
                    hospital.available_beds,

                "Status":
                    hospital.status,

                "Latitude":
                    hospital.latitude,

                "Longitude":
                    hospital.longitude,

                "Created At":
                    (
                        hospital.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if hospital.created_at
                        else "N/A"
                    )
            }
        )


    st.dataframe(
        hospital_data,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # HOSPITAL MANAGEMENT
    # ========================================================

    st.divider()

    st.header("🛠️ Hospital Management")


    hospital_ids = [
        hospital.id
        for hospital in hospitals
    ]


    selected_id = st.selectbox(
        "Select Hospital",
        hospital_ids
    )


    selected_hospital = next(
        (
            hospital
            for hospital in hospitals
            if hospital.id == selected_id
        ),
        None
    )


    if selected_hospital:

        # ====================================================
        # UPDATE HOSPITAL
        # ====================================================

        st.subheader(
            f"✏️ Update Hospital #{selected_hospital.id}"
        )


        with st.form(
            f"update_hospital_{selected_hospital.id}"
        ):

            col1, col2 = st.columns(2)


            with col1:

                update_name = st.text_input(
                    "Hospital Name",
                    value=selected_hospital.name
                )


                update_city = st.text_input(
                    "City",
                    value=selected_hospital.city
                )


                update_status = st.selectbox(
                    "Status",
                    HOSPITAL_STATUSES,
                    index=(
                        HOSPITAL_STATUSES.index(
                            selected_hospital.status
                        )
                        if selected_hospital.status
                        in HOSPITAL_STATUSES
                        else 0
                    )
                )


            with col2:

                update_total_beds = st.number_input(
                    "Total Beds",
                    min_value=1,
                    max_value=100000,
                    value=int(
                        selected_hospital.total_beds
                    ),
                    step=1
                )


                update_available_beds = st.number_input(
                    "Available Beds",
                    min_value=0,
                    max_value=100000,
                    value=int(
                        selected_hospital.available_beds
                    ),
                    step=1
                )


            # ------------------------------------------------
            # COORDINATES
            # ------------------------------------------------

            col1, col2 = st.columns(2)


            with col1:

                update_latitude = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=float(
                        selected_hospital.latitude
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
                        selected_hospital.longitude
                        or 78.4867
                    ),
                    format="%.6f"
                )


            update_button = st.form_submit_button(
                "💾 Update Hospital",
                type="primary"
            )


        # ====================================================
        # SAVE UPDATE
        # ====================================================

        if update_button:

            if not update_name.strip():

                st.error(
                    "Hospital name cannot be empty."
                )

            elif not update_city.strip():

                st.error(
                    "City cannot be empty."
                )

            elif update_available_beds > update_total_beds:

                st.error(
                    "Available beds cannot exceed total beds."
                )

            else:

                db = SessionLocal()

                try:

                    hospital = (
                        db.query(Hospital)
                        .filter(
                            Hospital.id
                            == selected_hospital.id
                        )
                        .first()
                    )


                    if hospital:

                        # Check duplicate name.
                        duplicate = (
                            db.query(Hospital)
                            .filter(
                                Hospital.name
                                == update_name.strip(),

                                Hospital.id
                                != selected_hospital.id
                            )
                            .first()
                        )


                        if duplicate:

                            st.error(
                                "Another hospital already "
                                "uses this name."
                            )

                        else:

                            hospital.name = (
                                update_name.strip()
                            )

                            hospital.city = (
                                update_city.strip()
                            )

                            hospital.status = (
                                update_status
                            )

                            hospital.total_beds = (
                                int(
                                    update_total_beds
                                )
                            )

                            hospital.available_beds = (
                                int(
                                    update_available_beds
                                )
                            )

                            hospital.latitude = (
                                float(
                                    update_latitude
                                )
                            )

                            hospital.longitude = (
                                float(
                                    update_longitude
                                )
                            )


                            db.commit()


                            st.success(
                                f"✅ Hospital #{hospital.id} "
                                "updated successfully."
                            )


                            st.rerun()


                except Exception as error:

                    db.rollback()

                    st.error(
                        "❌ Failed to update hospital."
                    )

                    st.exception(
                        error
                    )

                finally:

                    db.close()


        # ====================================================
        # QUICK BED UPDATE
        # ====================================================

        st.subheader(
            "🛏️ Quick Bed Availability Update"
        )


        with st.form(
            f"bed_form_{selected_hospital.id}"
        ):

            new_available_beds = st.number_input(
                "New Available Beds",
                min_value=0,
                max_value=selected_hospital.total_beds,
                value=int(
                    selected_hospital.available_beds
                ),
                step=1
            )


            update_beds_button = st.form_submit_button(
                "🛏️ Update Beds"
            )


        if update_beds_button:

            db = SessionLocal()

            try:

                hospital = (
                    db.query(Hospital)
                    .filter(
                        Hospital.id
                        == selected_hospital.id
                    )
                    .first()
                )


                if hospital:

                    hospital.available_beds = (
                        int(
                            new_available_beds
                        )
                    )


                    db.commit()


                    st.success(
                        f"✅ Available beds updated to "
                        f"{new_available_beds}."
                    )


                    st.rerun()


            except Exception as error:

                db.rollback()

                st.error(
                    "❌ Failed to update bed availability."
                )

                st.exception(
                    error
                )

            finally:

                db.close()


        # ====================================================
        # DELETE HOSPITAL
        # ====================================================

        st.subheader(
            f"🗑️ Delete Hospital #{selected_hospital.id}"
        )


        confirm_delete = st.checkbox(
            "I confirm that I want to permanently delete this hospital."
        )


        if st.button(
            "🗑️ Delete Selected Hospital",
            disabled=not confirm_delete
        ):

            db = SessionLocal()

            try:

                hospital = (
                    db.query(Hospital)
                    .filter(
                        Hospital.id
                        == selected_hospital.id
                    )
                    .first()
                )


                if hospital:

                    db.delete(
                        hospital
                    )

                    db.commit()


                    st.success(
                        f"✅ Hospital #{selected_hospital.id} "
                        "deleted successfully."
                    )


                    st.rerun()


            except Exception as error:

                db.rollback()

                st.error(
                    "❌ Failed to delete hospital."
                )

                st.exception(
                    error
                )

            finally:

                db.close()


    # ========================================================
    # HOSPITAL DETAILS
    # ========================================================

    st.divider()

    st.header("🔎 Hospital Details")


    for hospital in hospitals:

        with st.expander(
            f"🏥 Hospital #{hospital.id} | "
            f"{hospital.name} | "
            f"{hospital.status}"
        ):

            col1, col2 = st.columns(2)


            with col1:

                st.write(
                    "**Hospital ID:**",
                    hospital.id
                )

                st.write(
                    "**Hospital Name:**",
                    hospital.name
                )

                st.write(
                    "**City:**",
                    hospital.city
                )

                st.write(
                    "**Status:**",
                    hospital.status
                )


            with col2:

                st.write(
                    "**Total Beds:**",
                    hospital.total_beds
                )

                st.write(
                    "**Available Beds:**",
                    hospital.available_beds
                )

                st.write(
                    "**Latitude:**",
                    hospital.latitude
                )

                st.write(
                    "**Longitude:**",
                    hospital.longitude
                )


            if hospital.created_at:

                st.write(
                    "**Created At:**",
                    hospital.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )


else:

    st.info(
        "No hospitals have been added yet."
    )