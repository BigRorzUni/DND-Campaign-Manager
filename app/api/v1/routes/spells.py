from fastapi import APIRouter, Query
from app.services.spell_dataset import SpellDatasetService

router = APIRouter(prefix="/spells", tags=["spells"])


@router.get("")
def list_spells(q: str | None = Query(default=None)):
    if q:
        return SpellDatasetService.search_spells(q)
    return SpellDatasetService.list_spells()


@router.get("/{spell_index}")
def get_spell(spell_index: str):
    return SpellDatasetService.get_spell(spell_index)