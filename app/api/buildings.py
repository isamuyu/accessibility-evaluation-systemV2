from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import *
from app.services.crud import BuildingService

router = APIRouter(prefix="/buildings", tags=["建筑管理"])

@router.post("/", response_model=BuildingResponse)
def create_building(building: BuildingCreate, db: Session = Depends(get_db)):
    return BuildingService.create(db, building)

@router.get("/project/{project_id}", response_model=List[BuildingResponse])
def list_buildings_by_project(project_id: str, db: Session = Depends(get_db)):
    return BuildingService.get_by_project(db, project_id)

@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(building_id: str, db: Session = Depends(get_db)):
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return building

@router.put("/{building_id}", response_model=BuildingResponse)
def update_building(building_id: str, building: BuildingUpdate, db: Session = Depends(get_db)):
    db_obj = BuildingService.get(db, building_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return BuildingService.update(db, db_obj, building)
@router.delete("/{building_id}")
def delete_building(building_id: str, db: Session = Depends(get_db)):
    db_obj = BuildingService.get(db, building_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="建筑不存在")
    BuildingService.delete(db, db_obj)
    return {"message": "建筑已删除"}
