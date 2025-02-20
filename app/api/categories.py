from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, Float
from typing import List, Optional

from ..database import get_db, get_last_query_duration
from ..models import Category, App
from ..schemas import ResponseModel
from ..schemas import CategoryCreate, Category as CategorySchema, CategoryWithApps

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/{category_id}/rating")
async def get_category_rating(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get the average rating for a specific category."""
    result = (
        db.query(func.avg(App.rating).cast(Float))
        .filter(App.category_id == category_id)
        .scalar()
    )
    
    return {'data' : {"average_rating": round(result, 2) if result else 0}, 'metadata': {'query_duration_ms': get_last_query_duration()}}

@router.get("/", response_model=ResponseModel[List[CategorySchema]])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Category)
    if name:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    return { 'data': query.offset(skip).limit(limit).all(), 'metadata': {'query_duration_ms': get_last_query_duration()} }

@router.post("/", response_model=ResponseModel[CategorySchema])
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    db_category = Category(**category.model_dump())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return {
            'data': db_category,
            'metadata': {'query_duration_ms': get_last_query_duration() }
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )

@router.get("/{category_id}", response_model=ResponseModel[CategoryWithApps])
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    try:
        for key, value in category.model_dump().items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )

@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    try:
        db.delete(category)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category as it has associated apps"
        )
