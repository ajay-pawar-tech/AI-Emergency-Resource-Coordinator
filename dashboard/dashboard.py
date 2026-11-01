import sys
from pathlib import Path
import streamlit as st
from streamlit_js_eval import get_geolocation
import uuid
from PIL import Image, ImageOps


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

from app.services.llm_service import analyze_emergency_image
from app.agents.coordinator_agent import coordinate_emergency
from app.database.db import SessionLocal
from app.database.repositories.incident_repository import IncidentRepository
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
# AI EMERGENCY IMAGE ANALYSIS
# ============================================================

st.divider()

st.header("📸 AI Emergency Image Detection")

st.write(
    "Upload an emergency image and let AI analyze the visible "
    "emergency situation."
)


uploaded_image = st.file_uploader(
    "Upload Emergency Image",
    type=["jpg", "jpeg", "png"],
    help="Upload an image showing a possible emergency situation."
)

if uploaded_image is not None:

    max_file_size = 10 * 1024 * 1024  # 10 MB

    if uploaded_image.size > max_file_size:

        st.error(
            "❌ Image is too large. "
            "Please upload an image smaller than 10 MB."
        )

        st.stop()
# ============================================================
# REAL DEVICE LOCATION
# ============================================================

location_data = get_geolocation()

if location_data:
    gps_latitude = location_data.get("coords", {}).get("latitude")
    gps_longitude = location_data.get("coords", {}).get("longitude")
else:
    gps_latitude = None
    gps_longitude = None

if gps_latitude is not None and gps_longitude is not None:
    st.success(
        f"📍 GPS Location detected: "
        f"{gps_latitude:.6f}, {gps_longitude:.6f}"
    )
else:
    st.warning(
        "📍 GPS location not available. "
        "Please allow location access in your browser."
    )

if uploaded_image:

    st.image(
        uploaded_image,
        caption="Uploaded Emergency Image",
        use_container_width=True
    )


    analyze_image = st.button(
        "🤖 Analyze Emergency Image",
        type="secondary",
        use_container_width=True
    )


    if analyze_image:

        with st.spinner(
            "🤖 AI is analyzing the emergency image..."
        ):

            # ------------------------------------------------
            # SAVE UPLOADED IMAGE
            # ------------------------------------------------

            temp_image_path = (
                BASE_DIR / f"uploaded_emergency_image_{uuid.uuid4().hex}.jpg"
            )


            with open(
                temp_image_path,
                "wb"
            ) as image_file:

                image_file.write(
                    uploaded_image.getbuffer()
                )


            # ------------------------------------------------
            # RUN AI ANALYSIS
            # ------------------------------------------------

            image_analysis = analyze_emergency_image(
                temp_image_path
            )


            # Remove temporary uploaded image after AI analysis
            try:
                temp_image_path.unlink(missing_ok=True)
            except Exception:
                pass


        # ----------------------------------------------------
        # CHECK ANALYSIS RESULT
        # ----------------------------------------------------

        if image_analysis.get(
            "success",
            False
        ):

            st.success(
                "✅ Emergency image analysis completed."
            )


            # ------------------------------------------------
            # GET STRUCTURED AI ANALYSIS
            # ------------------------------------------------

            analysis_data = image_analysis.get(
                "analysis",
                {}
            )


            # ------------------------------------------------
            # VALIDATE AI ANALYSIS
            # ------------------------------------------------

            required_fields = [
                "incident_type",
                "severity",
                "possible_victims",
                "description"
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in analysis_data
            ]

            if missing_fields:

                st.error(
                    "❌ AI returned incomplete emergency information."
                )

                st.warning(
                    f"Missing fields: {', '.join(missing_fields)}"
                )

                st.stop()


            # ------------------------------------------------
            # CREATE INCIDENT DATA FROM AI ANALYSIS
            # ------------------------------------------------

            incident_data = {
                "incident_type": analysis_data.get(
                    "incident_type",
                    "Unknown"
                ),

                "severity": analysis_data.get(
                    "severity",
                    "Unknown"
                ),

                "victims": analysis_data.get(
                    "possible_victims",
                    0
                ),

                "vehicles_detected": analysis_data.get(
                    "vehicles_detected",
                    0
                ),

                "visible_hazards": analysis_data.get(
                    "visible_hazards",
                    []
                ),

                "description": analysis_data.get(
                    "description",
                    ""
                ),

                "ai_confidence": analysis_data.get(
                    "confidence",
                    0
                )
            }


            # ------------------------------------------------
            # SAVE INCIDENT DATA IN SESSION STATE
            # ------------------------------------------------

            # IMPORTANT:
            # Streamlit reruns the whole script on every button
            # or checkbox click, so the AI analysis and incident
            # data must be stored in session_state.

            st.session_state["incident_data"] = incident_data

            st.session_state["analysis_data"] = analysis_data

            # New AI analysis must require fresh human confirmation.
            st.session_state["incident_confirmed"] = False

            st.session_state["confirm_emergency_checkbox"] = False

            # New analysis = new incident, so the old saved
            # incident id must be cleared.
            st.session_state.pop("incident_id", None)


        else:

            st.error(
                "❌ Emergency image analysis failed."
            )

            error_message = image_analysis.get(
                "error",
                "Unknown error."
            )

            st.warning(error_message)

            if image_analysis.get("error_type") == "temporary_unavailable":

                st.info(
                    "Gemini Vision is temporarily busy. "
                    "Please try the analysis again."
                )

                if st.button(
                    "🔄 Retry Image Analysis",
                    key="retry_image_analysis"
                ):
                    st.rerun()


# ============================================================
# DISPLAY AI ANALYSIS + HUMAN CONFIRMATION
# ============================================================

# This block is outside the "Analyze" button block on purpose.
# When the checkbox is clicked, Streamlit reruns the script and
# the "Analyze" button becomes False, so the analysis and the
# checkbox must be shown from session_state.

if "analysis_data" in st.session_state:

    analysis_data = st.session_state["analysis_data"]


    # --------------------------------------------------------
    # DISPLAY EMERGENCY INFORMATION
    # --------------------------------------------------------

    st.subheader(
        "🤖 AI Emergency Analysis"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Incident Type",
            analysis_data.get(
                "incident_type",
                "Unknown"
            )
        )


        st.metric(
            "Severity",
            analysis_data.get(
                "severity",
                "Unknown"
            )
        )


        st.metric(
            "Possible Victims",
            analysis_data.get(
                "possible_victims",
                "Unknown"
            )
        )


    with col2:

        st.metric(
            "Vehicles Detected",
            analysis_data.get(
                "vehicles_detected",
                "Unknown"
            )
        )


        st.metric(
    "AI Confidence",
    (
        f"{min(max(float(analysis_data.get('confidence', 0)), 0), 1) * 100:.1f}%"
        if isinstance(
            analysis_data.get("confidence"),
            (int, float)
        )
        else "Unknown"
    )
)

    # --------------------------------------------------------
    # VISIBLE HAZARDS
    # --------------------------------------------------------

    st.markdown(
        "### ⚠️ Visible Hazards"
    )


    hazards = analysis_data.get(
        "visible_hazards",
        []
    )


    if hazards:

        for hazard in hazards:

            st.write(
                f"• {hazard}"
            )

    else:

        st.write(
            "No visible hazards identified."
        )


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    st.markdown(
        "### 📝 AI Description"
    )


    st.write(
        analysis_data.get(
            "description",
            "No description available."
        )
    )


    # --------------------------------------------------------
    # HUMAN CONFIRMATION
    # --------------------------------------------------------

    st.subheader("👤 Human Confirmation")

    st.warning(
        "Please review the AI-detected emergency details "
        "before starting emergency coordination."
    )

    confirm_emergency = st.checkbox(
        "I confirm that the AI emergency analysis is correct.",
        key="confirm_emergency_checkbox"
    )

    st.session_state["incident_confirmed"] = confirm_emergency

    if confirm_emergency:

        st.success(
            "✅ Emergency analysis confirmed by human."
        )


        # ----------------------------------------------------
        # GET INCIDENT DATA FROM SESSION STATE
        # ----------------------------------------------------

        # IMPORTANT:
        # incident_data is only a local variable in the
        # "Analyze" button block. After the checkbox click the
        # script reruns, so it must be read from session_state.

        incident_data = st.session_state["incident_data"]


        # ----------------------------------------------------
        # PREVENT DUPLICATE INCIDENT CREATION
        # ----------------------------------------------------

        if "incident_id" in st.session_state:

            st.info(
                f"ℹ️ Incident #{st.session_state['incident_id']} "
                "has already been saved."
            )

        else:

            # ------------------------------------------------
            # SAVE CONFIRMED INCIDENT TO DATABASE
            # ------------------------------------------------

            db = None

            try:

                db = SessionLocal()

                # NOTE:
                # coordinate_emergency() raises an error when the
                # latest incident has no coordinates, so default
                # Hyderabad coordinates are saved here.
                # Replace them with real GPS values when available.

                incident_record = {
                    "incident_type": incident_data["incident_type"],
                    "severity": incident_data["severity"],
                    "city": "Hyderabad",
                    "location": "AI detected emergency location",
                    "latitude": gps_latitude,
                    "longitude": gps_longitude,
                    "victims": incident_data["victims"],
                    "critical_victims": 0,
                    "description": incident_data["description"],
                    "status": "Active",
                }

                saved_incident = IncidentRepository.create(
                    db,
                    incident_record
                )

                st.session_state["incident_id"] = saved_incident.id

                st.success(
                    f"✅ Incident #{saved_incident.id} saved to database."
                )

            except Exception as error:

                st.error(
                    "❌ Failed to save incident to database."
                )

                st.exception(error)

            finally:

                if db is not None:
                    db.close()


# ============================================================
# COORDINATION WORKFLOW
# ============================================================

if run_coordination:

    # --------------------------------------------------------
    # CHECK AI INCIDENT DATA
    # --------------------------------------------------------

    if "incident_data" not in st.session_state:

        st.warning(
            "Please analyze an emergency image before running coordination."
        )

        st.stop()


    # --------------------------------------------------------
    # CHECK HUMAN CONFIRMATION
    # --------------------------------------------------------

    if not st.session_state.get("incident_confirmed", False):

        st.warning(
            "Please confirm the AI emergency analysis before running coordination."
        )

        st.stop()


    # --------------------------------------------------------
    # CHECK SAVED INCIDENT
    # --------------------------------------------------------

    if "incident_id" not in st.session_state:

        st.error(
            "❌ No saved incident found. "
            "Please confirm the AI analysis again."
        )

        st.stop()


    # --------------------------------------------------------
    # RUN COORDINATION
    # --------------------------------------------------------

    try:

        with st.spinner("Running emergency coordination..."):

            result = coordinate_emergency(
                incident_data=st.session_state["incident_data"],
                incident_id=st.session_state["incident_id"]
            )

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

    latitude = current_incident.get("latitude")
    longitude = current_incident.get("longitude")

    st.info(
        f"📍 Location: "
        f"{current_incident.get('location', 'N/A')}, "
        f"{current_incident.get('city', 'N/A')}\n\n"
        f"🌐 GPS Coordinates: "
        f"{latitude:.6f}, {longitude:.6f}"
        if latitude is not None and longitude is not None
        else
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

    recommendation_data = result.get(
        "gemini_recommendation",
        {}
    )

    if isinstance(recommendation_data, dict):

        recommendation = recommendation_data.get(
            "recommendation",
            {}
        )

        if recommendation:

            st.info(
                f"🚨 {recommendation.get('summary', 'No summary available.')}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### 🚑 Ambulance")

                st.write(
                    f"**Vehicle:** "
                    f"{recommendation.get('recommended_ambulance', 'N/A')}"
                )

                st.write(
                    f"**Distance:** "
                    f"{recommendation.get('route_distance_km', 'N/A')} km"
                )

            with col2:

                st.markdown("### 🏥 Hospital")

                st.write(
                    f"**Hospital:** "
                    f"{recommendation.get('recommended_hospital', 'N/A')}"
                )

            col3, col4 = st.columns(2)

            with col3:

                st.markdown("### 🚒 Rescue Team")

                st.write(
                    f"**Team:** "
                    f"{recommendation.get('recommended_rescue_team', 'N/A')}"
                )

            with col4:

                st.markdown("### 🗺️ Route")

                st.write(
                    f"**Distance:** "
                    f"{recommendation.get('route_distance_km', 'N/A')} km"
                )

                st.write(
                    f"**Estimated Travel Time:** "
                    f"{recommendation.get('estimated_travel_time_minutes', 'N/A')} minutes"
                )

            st.markdown("### ⚠️ Immediate Action")

            st.warning(
                recommendation.get(
                    "immediate_action",
                    "No immediate action available."
                )
            )

            st.caption(
                f"AI Provider: "
                f"{recommendation_data.get('provider', 'Unknown')}"
            )

        else:

            st.warning(
                "AI recommendation data is unavailable."
            )

    else:

        st.warning(
            "AI recommendation is unavailable."
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
