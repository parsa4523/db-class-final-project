from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from datetime import date

from ..database import get_db, get_last_query_duration
from ..models import App, Category, Developer
from ..schemas import AppCreate, AppDetail, AppList, ResponseModel

router = APIRouter(
    prefix="/apps",
    tags=["apps"]
)

@router.get("/yearly-stats/{category_id}")
async def get_yearly_statistics(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get yearly statistics for released and updated apps in a category."""
    
    # Query for released apps count per year
    released_query = (
        db.query(
            extract('year', App.released_date).label('year'),
            func.count().label('count')
        )
        .filter(App.category_id == category_id)
        .group_by(extract('year', App.released_date))
    )
    
    print("\n=== Released Apps SQL Query ===")
    print(released_query.statement.compile(compile_kwargs={"literal_binds": True}))
    print("========================\n")
    
    released_stats = released_query.all()
    
    # Query for updated apps count per year
    updated_query = (
        db.query(
            extract('year', App.last_updated).label('year'),
            func.count().label('count')
        )
        .filter(App.category_id == category_id)
        .group_by(extract('year', App.last_updated))
    )
    
    print("\n=== Updated Apps SQL Query ===")
    print(updated_query.statement.compile(compile_kwargs={"literal_binds": True}))
    print("========================\n")
    
    updated_stats = updated_query.all()
    
    # Convert to dictionary format
    result = {
        'data': {
            'released': {int(year): count for year, count in released_stats if year},
            'updated': {int(year): count for year, count in updated_stats if year}
        },
        'metadata': {
            'query_duration_ms': get_last_query_duration()
        }
    }
    
    return result

@router.get("/", response_model=ResponseModel[List[AppList]])
async def list_apps(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    developer_id: Optional[int] = None,
    is_free: Optional[bool] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    content_rating: Optional[str] = None,
    has_ads: Optional[bool] = None,
    is_editors_choice: Optional[bool] = None,
    released_after: Optional[date] = None,
    released_before: Optional[date] = None,
    sort_by: Optional[str] = Query(
        None,
        description="Sort field (rating, rating_count, released_date, last_updated)",
    ),
    order: Optional[str] = Query(
        "desc",
        regex="^(asc|desc)$",
        description="Sort order (asc, desc)",
    ),
    db: Session = Depends(get_db)
):
    query = db.query(
        App.id,
        App.name,
        App.app_id,
        App.rating,
        App.rating_count,
        App.installs,
        App.is_free,
        App.price,
        App.released_date,
        App.last_updated,
        App.content_rating,
        App.category_id,
        App.developer_id
    )
    
    # Apply index-optimized filters first
    if is_free is not None:
        query = query.filter(App.is_free == is_free)
    if category_id is not None:
        query = query.filter(App.category_id == category_id)
    if min_rating:
        query = query.filter(App.rating >= min_rating)
        
    # Apply remaining filters
    if name:
        query = query.filter(App.name.ilike(f"%{name}%"))
    if developer_id:
        query = query.filter(App.developer_id == developer_id)
    if content_rating:
        query = query.filter(App.content_rating == content_rating)
    if has_ads is not None:
        query = query.filter(App.has_ads == has_ads)
    if is_editors_choice is not None:
        query = query.filter(App.is_editors_choice == is_editors_choice)
    if released_after:
        query = query.filter(App.released_date >= released_after)
    if released_before:
        query = query.filter(App.released_date <= released_before)
    
    # Apply sorting
    if sort_by:
        sort_column = getattr(App, sort_by, None)
        if sort_column:
            query = query.order_by(
                sort_column.desc() if order == "desc" else sort_column.asc()
            )
    
    # Print the generated SQL query
    print("\n=== Generated SQL Query ===")
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    print("========================\n")
    
    apps = query.offset(skip).limit(limit).all()
    return {
        'data': apps,
        'metadata': {
            'query_duration_ms': get_last_query_duration()
        }
    }

@router.post("/")
async def create_app(
    app: AppCreate,
    db: Session = Depends(get_db)
):
    # Verify category and developer exist
    category = db.query(Category).filter(Category.id == app.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    developer = db.query(Developer).filter(Developer.id == app.developer_id).first()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    db_app = App(**app.model_dump())
    try:
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        return {
        'data': db_app,
        'metadata': {
            'query_duration_ms': get_last_query_duration()
        }
    }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="App with this app_id already exists"
        )

@router.get("/{app_id}")
async def get_app(
    app_id: int,
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return {
        'data': app,
        'metadata': {
            'query_duration_ms': get_last_query_duration()
        }
    }

@router.put("/{app_id}")
async def update_app(
    app_id: int,
    app: AppCreate,
    db: Session = Depends(get_db)
):
    # Verify category and developer exist
    category = db.query(Category).filter(Category.id == app.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    developer = db.query(Developer).filter(Developer.id == app.developer_id).first()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    db_app = db.query(App).filter(App.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    
    try:
        for key, value in app.model_dump().items():
            setattr(db_app, key, value)
        db.commit()
        db.refresh(db_app)
        return {
            'data': db_app,
            'metadata': {
                'query_duration_ms': get_last_query_duration()
            }
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="App with this app_id already exists"
        )

@router.delete("/{app_id}", status_code=204)
async def delete_app(
    app_id: int,
    db: Session = Depends(get_db)
):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db.delete(app)
    db.commit()

@router.get("/search/")
async def search_apps(
    q: str = Query(..., min_length=3, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search apps by name, category name, or developer name
    """
    query = (
        db.query(
            App.id,
            App.name,
            App.app_id,
            App.rating,
            App.rating_count,
            App.installs,
            App.is_free,
            App.price,
            App.released_date,
            App.last_updated,
            App.content_rating,
            App.category_id,
            App.developer_id
        )
        .join(Category)
        .join(Developer)
        .filter(
            or_(
                App.name.ilike(f"%{q}%"),
                Category.name.ilike(f"%{q}%"),
                Developer.name.ilike(f"%{q}%")
            )
        )
    )
    apps = query.offset(skip).limit(limit).all()
    return {
        'data': apps,
        'metadata': {
            'query_duration_ms': get_last_query_duration()
        }
    }
