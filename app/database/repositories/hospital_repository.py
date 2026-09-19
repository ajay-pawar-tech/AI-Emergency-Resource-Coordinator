from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Hospital


class HospitalRepository:
    """
    Repository layer for Hospital CRUD operations.
    """

    @staticmethod
    def create(db: Session, hospital_data: dict) -> Hospital:
        """Create a new hospital."""

        hospital = Hospital(**hospital_data)

        db.add(hospital)
        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def get_by_id(
        db: Session,
        hospital_id: int
    ) -> Optional[Hospital]:
        """Get one hospital by ID."""

        return (
            db.query(Hospital)
            .filter(Hospital.id == hospital_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[Hospital]:
        """Get hospitals with pagination."""

        return (
            db.query(Hospital)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        hospital_id: int,
        update_data: dict
    ) -> Optional[Hospital]:
        """Update an existing hospital."""

        hospital = (
            db.query(Hospital)
            .filter(Hospital.id == hospital_id)
            .first()
        )

        if hospital is None:
            return None

        allowed_fields = {
            "name",
            "city",
            "latitude",
            "longitude",
            "total_beds",
            "available_beds",
            "status",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(hospital, field, value)

        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def delete(
        db: Session,
        hospital_id: int
    ) -> bool:
        """Delete a hospital by ID."""

        hospital = (
            db.query(Hospital)
            .filter(Hospital.id == hospital_id)
            .first()
        )

        if hospital is None:
            return False

        db.delete(hospital)
        db.commit()

        return True