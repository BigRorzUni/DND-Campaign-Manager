from fastapi import APIRouter, Query, HTTPException

from app.services.monster_dataset import MonsterDatasetService


router = APIRouter(prefix="/monsters", tags=["monsters"])


@router.get("")
def search_monsters(q: str | None = Query(default=None)):
    return MonsterDatasetService.search_monsters(q)


@router.get("/{monster_index}")
def get_monster(monster_index: str):
    monster = MonsterDatasetService.get_monster(monster_index)

    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")

    return monster