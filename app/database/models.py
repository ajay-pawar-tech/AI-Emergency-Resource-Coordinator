from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.database.db import Base


# ============================================================
# INCIDENT MODEL
# ============================================================

class Incident(Base):

    # Define the database table name.
    __tablename__ = "incidents"

    # Define the primary key.
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Store the emergency incident type.
    incident_type = Column(
        String(100),
        nullable=False
    )

    # Store the emergency severity.
    severity = Column(
        String(50),
        nullable=False
    )

    # Store the city where the incident occurred.
    city = Column(
        String(100),
        nullable=False
    )

    # Store the incident location or area.
    location = Column(
        String(255),
        nullable=False
    )

    # Store the incident latitude.
    latitude = Column(
        Float,
        nullable=True
    )

    # Store the incident longitude.
    longitude = Column(
        Float,
        nullable=True
    )

    # Store the total number of victims.
    victims = Column(
        Integer,
        default=0,
        nullable=False
    )

    # Store the number of critical victims.
    critical_victims = Column(
        Integer,
        default=0,
        nullable=False
    )

    # Store additional incident details.
    description = Column(
        Text,
        nullable=True
    )

    # Store the current incident status.
    status = Column(
        String(50),
        default="Active",
        nullable=False
    )

    # Store the incident creation time.
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ============================================================
# HOSPITAL MODEL
# ============================================================

class Hospital(Base):

    # Define the database table name.
    __tablename__ = "hospitals"

    # Define the primary key.
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Store the hospital name.
    name = Column(
        String(150),
        nullable=False
    )

    # Store the hospital city.
    city = Column(
        String(100),
        nullable=False
    )

    # Store the hospital latitude.
    latitude = Column(
        Float,
        nullable=True
    )

    # Store the hospital longitude.
    longitude = Column(
        Float,
        nullable=True
    )

    # Store the total number of beds.
    total_beds = Column(
        Integer,
        nullable=False
    )

    # Store the currently available beds.
    available_beds = Column(
        Integer,
        nullable=False
    )

    # Store the hospital status.
    status = Column(
        String(50),
        default="active",
        nullable=False
    )

    # Store the hospital creation time.
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ============================================================
# AMBULANCE MODEL
# ============================================================

class Ambulance(Base):

    # Define the database table name.
    __tablename__ = "ambulances"

    # Define the primary key.
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Store the ambulance vehicle number.
    vehicle_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    # Store the ambulance type.
    vehicle_type = Column(
        String(100),
        nullable=False
    )

    # Store the ambulance latitude.
    latitude = Column(
        Float,
        nullable=True
    )

    # Store the ambulance longitude.
    longitude = Column(
        Float,
        nullable=True
    )

    # Store the city where the ambulance operates.
    city = Column(
        String(100),
        nullable=False
    )

    # Store the ambulance status.
    status = Column(
        String(50),
        default="available",
        nullable=False
    )

    # Store the ambulance capacity.
    capacity = Column(
        Integer,
        default=1,
        nullable=False
    )

    # Store the ambulance creation time.
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ============================================================
# RESCUE TEAM MODEL
# ============================================================

class RescueTeam(Base):

    # Define the database table name.
    __tablename__ = "rescue_teams"

    # Define the primary key.
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Store the rescue team name.
    team_name = Column(
        String(150),
        unique=True,
        nullable=False
    )

    # Store the rescue team type.
    team_type = Column(
        String(100),
        nullable=False
    )

    # Store the number of team members.
    members = Column(
        Integer,
        default=0,
        nullable=False
    )

    # Store the rescue team's latitude.
    latitude = Column(
        Float,
        nullable=True
    )

    # Store the rescue team's longitude.
    longitude = Column(
        Float,
        nullable=True
    )

    # Store the city where the team operates.
    city = Column(
        String(100),
        nullable=False
    )

    # Store the rescue team status.
    status = Column(
        String(50),
        default="available",
        nullable=False
    )

    # Store the rescue team creation time.
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )