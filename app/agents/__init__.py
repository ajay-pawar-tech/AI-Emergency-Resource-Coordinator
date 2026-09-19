from app.database.db import Base, engine

# Import all database models.
from app.database.models import (
    Incident,
    Hospital,
    Ambulance,
    RescueTeam
)


# Create all database tables that do not already exist.
Base.metadata.create_all(
    bind=engine
)


# Display a success message.
print("Database tables created successfully.")