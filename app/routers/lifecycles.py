from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import Lifecycle
from app.schemas import LifecycleCreate, LifecycleResponse, LifecycleUpdate, PipelineStatsResponse

router = APIRouter(prefix="/api/lifecycles", tags=["lifecycles"])


@router.get("", response_model=list[LifecycleResponse])
def get_lifecycles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    contact_id: Optional[int] = None,
    ciclo_vida: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(Lifecycle)
    if contact_id:
        query = query.filter(Lifecycle.contact_id == contact_id)
    if ciclo_vida:
        query = query.filter(Lifecycle.ciclo_vida == ciclo_vida)
    return query.order_by(Lifecycle.fecha.desc()).offset(skip).limit(limit).all()


@router.get("/contact/{contact_id}", response_model=LifecycleResponse)
def get_latest_lifecycle_by_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    lifecycle = db.query(Lifecycle).filter(Lifecycle.contact_id == contact_id).order_by(Lifecycle.fecha.desc()).first()
    if not lifecycle:
        raise HTTPException(status_code=404, detail="Lifecycle not found for this contact")
    return lifecycle


@router.get("/{lifecycle_id}", response_model=LifecycleResponse)
def get_lifecycle(
    lifecycle_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    lifecycle = db.query(Lifecycle).filter(Lifecycle.id == lifecycle_id).first()
    if not lifecycle:
        raise HTTPException(status_code=404, detail="Lifecycle not found")
    return lifecycle


@router.post("", response_model=LifecycleResponse, status_code=status.HTTP_201_CREATED)
def create_lifecycle(
    lifecycle: LifecycleCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_lifecycle = Lifecycle(**lifecycle.model_dump())
    db.add(db_lifecycle)
    db.commit()
    db.refresh(db_lifecycle)
    return db_lifecycle


@router.put("/{lifecycle_id}", response_model=LifecycleResponse)
def update_lifecycle(
    lifecycle_id: int,
    lifecycle: LifecycleUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_lifecycle = db.query(Lifecycle).filter(Lifecycle.id == lifecycle_id).first()
    if not db_lifecycle:
        raise HTTPException(status_code=404, detail="Lifecycle not found")
    update_data = lifecycle.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lifecycle, field, value)
    db.commit()
    db.refresh(db_lifecycle)
    return db_lifecycle


@router.delete("/{lifecycle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lifecycle(
    lifecycle_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_lifecycle = db.query(Lifecycle).filter(Lifecycle.id == lifecycle_id).first()
    if not db_lifecycle:
        raise HTTPException(status_code=404, detail="Lifecycle not found")
    db.delete(db_lifecycle)
    db.commit()
    return None


@router.get("/stats/pipeline", response_model=PipelineStatsResponse)
def get_pipeline_stats(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    subquery = (
        db.query(Lifecycle.contact_id, Lifecycle.fecha)
        .distinct(Lifecycle.contact_id)
        .order_by(Lifecycle.contact_id, Lifecycle.fecha.desc())
        .subquery()
    )

    latest_lifecycles = (
        db.query(Lifecycle)
        .join(subquery, (Lifecycle.contact_id == subquery.c.contact_id) & (Lifecycle.fecha == subquery.c.fecha))
        .all()
    )

    total = len(latest_lifecycles)

    by_stage: dict[str, int] = {}
    for lifecycle in latest_lifecycles:
        stage_name = str(lifecycle.ciclo_vida)
        by_stage[stage_name] = by_stage.get(stage_name, 0) + 1

    return PipelineStatsResponse(
        total=total,
        by_stage=[{"stage": k, "count": v} for k, v in by_stage.items()],
    )
