from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.session_repo import SessionRepo
from app.repositories.encounter_repo import EncounterRepo
from app.schemas.encounter import EncounterCreate, EncounterOut, EncounterUpdate
from app.services.encounter_simulation_service import EncounterSimulationService

router = APIRouter(tags=["encounters"])
session_repo = SessionRepo()
encounter_repo = EncounterRepo()
simulation_service = EncounterSimulationService()


@router.post(
    "/sessions/{session_id}/encounters",
    response_model=EncounterOut,
    status_code=status.HTTP_201_CREATED,
)
def create_encounter(
    session_id: int,
    payload: EncounterCreate,
    db: DbSession = Depends(get_db),
):
    session = session_repo.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return encounter_repo.create(
        db,
        session_id=session_id,
        name=payload.name,
        expected_difficulty=payload.expected_difficulty,
        rounds=None,
        notes=payload.notes,
        is_simulated=payload.is_simulated,
        simulation_status="PENDING" if payload.is_simulated else None,
        winner=None,
    )


@router.get("/sessions/{session_id}/encounters", response_model=list[EncounterOut])
def list_encounters(session_id: int, db: DbSession = Depends(get_db)):
    session = session_repo.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return encounter_repo.list_for_session(db, session_id)


@router.get("/encounters/{encounter_id}", response_model=EncounterOut)
def get_encounter(encounter_id: int, db: DbSession = Depends(get_db)):
    obj = encounter_repo.get(db, encounter_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return obj


@router.put("/encounters/{encounter_id}", response_model=EncounterOut)
def update_encounter(
    encounter_id: int,
    payload: EncounterUpdate,
    db: DbSession = Depends(get_db),
):
    obj = encounter_repo.get(db, encounter_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return encounter_repo.update(
        db,
        obj,
        name=payload.name if payload.name is not None else obj.name,
        expected_difficulty=(
            payload.expected_difficulty
            if payload.expected_difficulty is not None
            else obj.expected_difficulty
        ),
        notes=payload.notes if payload.notes is not None else obj.notes,
        is_simulated=(
            payload.is_simulated
            if payload.is_simulated is not None
            else obj.is_simulated
        ),
        simulation_status=(
            payload.simulation_status
            if payload.simulation_status is not None
            else obj.simulation_status
        ),
        winner=payload.winner if payload.winner is not None else obj.winner,
    )


@router.post("/encounters/{encounter_id}/simulate", response_model=EncounterOut)
def simulate_encounter(encounter_id: int, db: DbSession = Depends(get_db)):
    encounter = encounter_repo.get(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    if not encounter.is_simulated:
        raise HTTPException(
            status_code=400,
            detail="Only simulated encounters can be auto-simulated",
        )

    simulation_service.run_simulation(db, encounter_id)

    updated = encounter_repo.get(db, encounter_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Encounter not found after simulation")

    return updated


@router.delete("/encounters/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_encounter(encounter_id: int, db: DbSession = Depends(get_db)):
    obj = encounter_repo.get(db, encounter_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Encounter not found")
    encounter_repo.delete(db, obj)