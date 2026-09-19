from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Incident


class IncidentRepository:
    """
    Repository layer for Incident CRUD operations.
    """

    @staticmethod
    def create(db: Session, incident_data: dict) -> Incident:
        """Create a new incident."""
        incident = Incident(**incident_data)

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    @staticmethod
    def get_by_id(
        db: Session,
        incident_id: int
    ) -> Optional[Incident]:
        """Get one incident by ID."""
        return (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[Incident]:
        """Get incidents with pagination."""
        return (
            db.query(Incident)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        incident_id: int,
        update_data: dict
    ) -> Optional[Incident]:
        """Update an existing incident."""

        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident is None:
            return None

        allowed_fields = {
            "incident_type",
            "severity",
            "city",
            "location",
            "latitude",
            "longitude",
            "victims",
            "critical_victims",
            "description",
            "status",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(incident, field, value)

        db.commit()
        db.refresh(incident)

        return incident

    @staticmethod
    def delete(
        db: Session,
        incident_id: int
    ) -> bool:
        """Delete an incident by ID."""

        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident is None:
            return False

        db.delete(incident)
        db.commit()

        return True