from fastapi import APIRouter, Query
from app.services.equipment_dataset import EquipmentDatasetService

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("")
def list_equipment(q: str | None = Query(default=None)):
    if q:
        return EquipmentDatasetService.search_equipment(q)
    return EquipmentDatasetService.list_equipment()


@router.get("/{equipment_index}")
def get_equipment(equipment_index: str):
    return EquipmentDatasetService.get_equipment(equipment_index)