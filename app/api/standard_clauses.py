from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.enums import Chapter
from app.schemas.schemas import *
from app.services.crud import StandardClauseService

router = APIRouter(prefix="/standard-clauses", tags=["标准条文"])

@router.post("/", response_model=StandardClauseResponse)
def create_clause(clause: StandardClauseCreate, db: Session = Depends(get_db)):
    return StandardClauseService.create(db, clause)

@router.get("/", response_model=List[StandardClauseResponse])
def list_clauses(skip: int = 0, limit: int = Query(default=100, le=1000), db: Session = Depends(get_db)):
    return StandardClauseService.get_multi(db, skip=skip, limit=limit)

@router.get("/chapter/{chapter}", response_model=List[StandardClauseResponse])
def get_clauses_by_chapter(chapter: Chapter, db: Session = Depends(get_db)):
    return StandardClauseService.get_by_chapter(db, chapter)

@router.get("/{clause_id}", response_model=StandardClauseResponse)
def get_clause(clause_id: str, db: Session = Depends(get_db)):
    clause = StandardClauseService.get(db, clause_id)
    if not clause:
        raise HTTPException(status_code=404, detail="标准条文不存在")
    return clause
@router.delete("/{clause_id}")
def delete_clause(clause_id: str, db: Session = Depends(get_db)):
    """软删除：标记为不活跃，保留历史评分数据引用"""
    clause = StandardClauseService.get(db, clause_id)
    if not clause:
        raise HTTPException(status_code=404, detail="标准条文不存在")
    clause.is_active = False
    db.commit()
    return {"message": "标准条文已停用"}
