from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db, get_last_query_duration
from ..models import Developer
from ..schemas import ResponseModel
from ..schemas import DeveloperCreate, Developer as DeveloperSchema, DeveloperWithApps

router = APIRouter(
    prefix="/developers",
    tags=["developers"]
)

@router.get("/", response_model=ResponseModel[List[DeveloperSchema]])
async def list_developers(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1),
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Developer)
    if name:
        query = query.filter(Developer.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Developer.email.ilike(f"%{email}%"))

    query_result = query.offset(skip).limit(limit).all()

    return { 'data': query_result, 'metadata': { 'query_duration_ms': get_last_query_duration() }}
    # return { 'data': , 'metadata': { 'query_duration_ms': get_last_query_duration()} }

@router.post("/", response_model=ResponseModel[DeveloperSchema])
async def create_developer(
    developer: DeveloperCreate,
    db: Session = Depends(get_db)
):
    db_developer = Developer(**developer.model_dump())
    try:
        db.add(db_developer)
        db.commit()
        db.refresh(db_developer)
        return { 'data': db_developer, 'metadata': { 'query_duration_ms': get_last_query_duration() }}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Developer with this name and email combination already exists"
        )

@router.get("/{developer_id}", response_model=DeveloperWithApps)
async def get_developer(
    developer_id: int,
    db: Session = Depends(get_db)
):
    developer = db.query(Developer).filter(Developer.id == developer_id).first()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer

@router.put("/{developer_id}", response_model=DeveloperSchema)
async def update_developer(
    developer_id: int,
    developer: DeveloperCreate,
    db: Session = Depends(get_db)
):
    db_developer = db.query(Developer).filter(Developer.id == developer_id).first()
    if not db_developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    try:
        for key, value in developer.model_dump().items():
            setattr(db_developer, key, value)
        db.commit()
        db.refresh(db_developer)
        return db_developer
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Developer with this name and email combination already exists"
        )

@router.delete("/{developer_id}", status_code=204)
async def delete_developer(
    developer_id: int,
    db: Session = Depends(get_db)
):
    developer = db.query(Developer).filter(Developer.id == developer_id).first()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    try:
        db.delete(developer)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete developer as they have associated apps"
        )
