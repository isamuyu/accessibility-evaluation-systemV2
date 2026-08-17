from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import *
from app.services.crud import ProjectService

router = APIRouter(prefix="/projects", tags=["项目管理"])

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create(db, project)

@router.get("/", response_model=List[ProjectResponse])
def list_projects(skip: int = 0, limit: int = Query(default=100, le=1000), db: Session = Depends(get_db)):
    return ProjectService.get_multi(db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_obj = ProjectService.get(db, project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectService.update(db, db_obj, project)
@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    db_obj = ProjectService.get(db, project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="项目不存在")
    if db_obj.buildings:
        raise HTTPException(status_code=400, detail="项目下存在建筑，无法删除")
    db.delete(db_obj)
    db.commit()
    return {"message": "项目已删除"}
