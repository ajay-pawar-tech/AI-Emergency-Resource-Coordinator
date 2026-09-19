import streamlit as st
import pandas as pd
import pydeck as pdk


def _get_coordinate(data, names):
    """
    Return the first available coordinate value
    from the given dictionary.
    """

    if not isinstance(data, dict):
        return None

    for name in names:

        value = data.get(name)

        if value is not None:
            return value

    return None


def _get_marker_color(resource_type):
    """
    Return marker color based on resource type.
    """

    colors = {
        "Incident": [220, 38, 38],
        "Ambulance": [37, 99, 235],
        "Hospital": [22, 163, 74],
        "Rescue Team": [245, 158, 11],
    }

    return colors.get(
        resource_type,
        [100, 100, 100]
    )


def display_emergency_map(result):
    """
    Display emergency incident and selected resources
    on an interactive map.
    """

    # ==========================================================
    # GET DATA
    # ==========================================================

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

    incident = result.get(
        "current_incident",
        {}
    )

    route = result.get(
        "route",
        {}
    )


    # ==========================================================
    # CREATE LOCATION DATA
    # ==========================================================

    locations = []


    # ==========================================================
    # INCIDENT COORDINATES
    # ==========================================================

    incident_lat = _get_coordinate(
        incident,
        [
            "latitude",
            "lat",
            "incident_latitude"
        ]
    )

    incident_lon = _get_coordinate(
        incident,
        [
            "longitude",
            "lon",
            "lng",
            "incident_longitude"
        ]
    )


    # ==========================================================
    # INCIDENT MARKER
    # ==========================================================

    if (
        incident_lat is not None
        and incident_lon is not None
    ):

        locations.append(
            {
                "name": "🚨 Emergency Incident",
                "details": (
                    f"{incident.get('incident_type', 'Incident')} | "
                    f"{incident.get('location', 'Unknown location')}"
                ),
                "latitude": float(incident_lat),
                "longitude": float(incident_lon),
                "type": "Incident",
                "color": _get_marker_color("Incident"),
            }
        )


    # ==========================================================
    # AMBULANCE COORDINATES
    # ==========================================================

    ambulance_lat = _get_coordinate(
        ambulance,
        [
            "latitude",
            "lat",
            "ambulance_latitude"
        ]
    )

    ambulance_lon = _get_coordinate(
        ambulance,
        [
            "longitude",
            "lon",
            "lng",
            "ambulance_longitude"
        ]
    )


    # ==========================================================
    # AMBULANCE MARKER
    # ==========================================================

    if (
        ambulance_lat is not None
        and ambulance_lon is not None
    ):

        locations.append(
            {
                "name": "🚑 Ambulance",
                "details": (
                    ambulance.get(
                        "vehicle_number",
                        "Unknown vehicle"
                    )
                ),
                "latitude": float(ambulance_lat),
                "longitude": float(ambulance_lon),
                "type": "Ambulance",
                "color": _get_marker_color("Ambulance"),
            }
        )


    # ==========================================================
    # HOSPITAL COORDINATES
    # ==========================================================

    hospital_lat = _get_coordinate(
        hospital,
        [
            "latitude",
            "lat",
            "hospital_latitude"
        ]
    )

    hospital_lon = _get_coordinate(
        hospital,
        [
            "longitude",
            "lon",
            "lng",
            "hospital_longitude"
        ]
    )


    # ==========================================================
    # HOSPITAL MARKER
    # ==========================================================

    if (
        hospital_lat is not None
        and hospital_lon is not None
    ):

        locations.append(
            {
                "name": "🏥 Hospital",
                "details": (
                    f"{hospital.get('name', 'Unknown hospital')} | "
                    f"Beds: {hospital.get('available_beds', 'N/A')}"
                ),
                "latitude": float(hospital_lat),
                "longitude": float(hospital_lon),
                "type": "Hospital",
                "color": _get_marker_color("Hospital"),
            }
        )


    # ==========================================================
    # RESCUE TEAM COORDINATES
    # ==========================================================

    rescue_lat = _get_coordinate(
        rescue_team,
        [
            "latitude",
            "lat",
            "rescue_latitude"
        ]
    )

    rescue_lon = _get_coordinate(
        rescue_team,
        [
            "longitude",
            "lon",
            "lng",
            "rescue_longitude"
        ]
    )


    # ==========================================================
    # RESCUE TEAM MARKER
    # ==========================================================

    if (
        rescue_lat is not None
        and rescue_lon is not None
    ):

        locations.append(
            {
                "name": "🚒 Rescue Team",
                "details": (
                    f"{rescue_team.get('team_name', 'Unknown team')} | "
                    f"{rescue_team.get('team_type', 'Unknown type')}"
                ),
                "latitude": float(rescue_lat),
                "longitude": float(rescue_lon),
                "type": "Rescue Team",
                "color": _get_marker_color("Rescue Team"),
            }
        )


    # ==========================================================
    # CHECK LOCATION DATA
    # ==========================================================

    if not locations:

        st.warning(
            "📍 No emergency location coordinates are available."
        )

        st.caption(
            "The map requires latitude and longitude values "
            "for the current incident and selected resources."
        )

        return


    # ==========================================================
    # CREATE DATAFRAME
    # ==========================================================

    map_data = pd.DataFrame(
        locations
    )


    # ==========================================================
    # MAP CENTER
    # ==========================================================

    center_lat = map_data["latitude"].mean()
    center_lon = map_data["longitude"].mean()


    # ==========================================================
    # MARKER LAYER
    # ==========================================================

    marker_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=[
            "longitude",
            "latitude"
        ],
        get_fill_color="color",
        get_radius=650,
        radius_min_pixels=8,
        radius_max_pixels=30,
        pickable=True,
        stroked=True,
        get_line_color=[
            255,
            255,
            255
        ],
        line_width_min_pixels=1,
    )


    # ==========================================================
    # ESTIMATED DISPATCH LINE
    # ==========================================================

    route_layers = []

    if (
        incident_lat is not None
        and incident_lon is not None
        and ambulance_lat is not None
        and ambulance_lon is not None
    ):

        route_data = pd.DataFrame(
            [
                {
                    "source": [
                        float(ambulance_lon),
                        float(ambulance_lat)
                    ],
                    "target": [
                        float(incident_lon),
                        float(incident_lat)
                    ],
                }
            ]
        )

        route_layer = pdk.Layer(
            "LineLayer",
            data=route_data,
            get_source_position="source",
            get_target_position="target",
            get_color=[
                239,
                68,
                68
            ],
            get_width=6,
            pickable=False,
        )

        route_layers.append(
            route_layer
        )


    # ==========================================================
    # MAP VIEW
    # ==========================================================

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
    )


    # ==========================================================
    # DISPLAY MAP
    # ==========================================================

    deck = pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=route_layers + [
            marker_layer
        ],
        tooltip={
            "html": (
                "<b>{name}</b><br/>"
                "{details}<br/>"
                "Type: {type}"
            ),
            "style": {
                "backgroundColor": "#111827",
                "color": "white",
                "fontSize": "14px",
                "padding": "8px",
            },
        },
    )

    st.pydeck_chart(
        deck,
        use_container_width=True,
    )


    # ==========================================================
    # MAP LEGEND
    # ==========================================================

    st.markdown(
        "### 📍 Map Legend"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            "🔴 **Emergency Incident**"
        )

    with col2:

        st.markdown(
            "🔵 **Ambulance**"
        )

    with col3:

        st.markdown(
            "🟢 **Hospital**"
        )

    with col4:

        st.markdown(
            "🟠 **Rescue Team**"
        )


    if (
        route
        and route.get("distance_km") is not None
        and route.get("time_minutes") is not None
    ):

        st.info(
            f"🚑 Estimated dispatch distance: "
            f"{route['distance_km']:.2f} km | "
            f"Estimated travel time: "
            f"{route['time_minutes']:.2f} min"
        )

        st.caption(
            "The line shown on this map is an estimated "
            "dispatch line between the selected ambulance "
            "and incident. It is not a road-by-road route."
        )


    # ==========================================================
    # LOCATION TABLE
    # ==========================================================

    st.markdown(
        "### 📋 Emergency Locations"
    )

    display_data = map_data[
        [
            "name",
            "type",
            "details",
            "latitude",
            "longitude"
        ]
    ].copy()

    display_data.columns = [
        "Resource",
        "Type",
        "Details",
        "Latitude",
        "Longitude"
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )