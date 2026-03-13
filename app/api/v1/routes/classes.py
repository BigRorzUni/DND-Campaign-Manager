from fastapi import APIRouter
from app.services.class_dataset import ClassDatasetService

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("")
def list_classes():
    return ClassDatasetService.list_classes()


@router.get("/{class_index}")
def get_class(class_index: str):
    return ClassDatasetService.get_class(class_index)