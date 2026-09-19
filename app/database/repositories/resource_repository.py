from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Ambulance, RescueTeam


class AmbulanceRepository:
    """Repository layer for Ambulance CRUD operations."""

    @staticmethod
    def create(db: Session, ambulance_data: dict) -> Ambulance:
        """Create a new ambulance."""

        ambulance = Ambulance(**ambulance_data)

        db.add(ambulance)
        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def get_by_id(
        db: Session,
        ambulance_id: int
    ) -> Optional[Ambulance]:
        """Get one ambulance by ID."""

        return (
            db.query(Ambulance)
            .filter(Ambulance.id == ambulance_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[Ambulance]:
        """Get ambulances with pagination."""

        return (
            db.query(Ambulance)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        ambulance_id: int,
        update_data: dict
    ) -> Optional[Ambulance]:
        """Update an existing ambulance."""

        ambulance = (
            db.query(Ambulance)
            .filter(Ambulance.id == ambulance_id)
            .first()
        )

        if ambulance is None:
            return None

        allowed_fields = {
            "vehicle_number",
            "vehicle_type",
            "latitude",
            "longitude",
            "city",
            "status",
            "capacity",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(ambulance, field, value)

        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def delete(
        db: Session,
        ambulance_id: int
    ) -> bool:
        """Delete an ambulance by ID."""

        ambulance = (
            db.query(Ambulance)
            .filter(Ambulance.id == ambulance_id)
            .first()
        )

        if ambulance is None:
            return False

        db.delete(ambulance)
        db.commit()

        return True


class RescueTeamRepository:
    """Repository layer for Rescue Team CRUD operations."""

    @staticmethod
    def create(db: Session, team_data: dict) -> RescueTeam:
        """Create a new rescue team."""

        team = RescueTeam(**team_data)

        db.add(team)
        db.commit()
        db.refresh(team)

        return team

    @staticmethod
    def get_by_id(
        db: Session,
        team_id: int
    ) -> Optional[RescueTeam]:
        """Get one rescue team by ID."""

        return (
            db.query(RescueTeam)
            .filter(RescueTeam.id == team_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[RescueTeam]:
        """Get rescue teams with pagination."""

        return (
            db.query(RescueTeam)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        team_id: int,
        update_data: dict
    ) -> Optional[RescueTeam]:
        """Update an existing rescue team."""

        team = (
            db.query(RescueTeam)
            .filter(RescueTeam.id == team_id)
            .first()
        )

        if team is None:
            return None

        allowed_fields = {
            "team_name",
            "team_type",
            "members",
            "latitude",
            "longitude",
            "city",
            "status",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(team, field, value)

        db.commit()
        db.refresh(team)

        return team

    @staticmethod
    def delete(
        db: Session,
        team_id: int
    ) -> bool:
        """Delete a rescue team by ID."""

        team = (
            db.query(RescueTeam)
            .filter(RescueTeam.id == team_id)
            .first()
        )

        if team is None:
            return False

        db.delete(team)
        db.commit()

        return True