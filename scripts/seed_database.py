from app.database.db import Base, engine
from app.database import models


def create_database():

    print("Creating database...")

    Base.metadata.create_all(bind=engine)

    print("Database created successfully!")


if __name__ == "__main__":
    create_database()