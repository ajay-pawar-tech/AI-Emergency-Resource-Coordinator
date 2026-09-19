from app.database.db import Base, engine

# Import all models so SQLAlchemy knows about
# every database table.
from app.database.models import (
    Incident,
    Hospital,
    Ambulance,
    RescueTeam,
)


def initialize_database():
    """
    Create all database tables if they do not already exist.
    """

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Database tables created successfully."
    )


if __name__ == "__main__":

    initialize_database()