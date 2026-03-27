from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import CSAT
from app.schemas import CSATAverageResponse, CSATByAgentResponse, CSATCreate, CSATResponse, CSATUpdate

router = APIRouter(prefix="/api/csat", tags=["csat"])


@router.get("", response_model=list[CSATResponse])
def get_csats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    team_id: Optional[int] = None,
    cesionario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(CSAT)
    if team_id:
        query = query.filter(CSAT.team_id == team_id)
    if cesionario_id:
        query = query.filter(CSAT.cesionario_id == cesionario_id)
    return query.order_by(CSAT.fecha.desc()).offset(skip).limit(limit).all()


@router.get("/{csat_id}", response_model=CSATResponse)
def get_csat(
    csat_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    csat = db.query(CSAT).filter(CSAT.id == csat_id).first()
    if not csat:
        raise HTTPException(status_code=404, detail="CSAT not found")
    return csat


@router.post("", response_model=CSATResponse, status_code=status.HTTP_201_CREATED)
def create_csat(
    csat: CSATCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_csat = CSAT(**csat.model_dump())
    db.add(db_csat)
    db.commit()
    db.refresh(db_csat)
    return db_csat


@router.put("/{csat_id}", response_model=CSATResponse)
def update_csat(
    csat_id: int,
    csat: CSATUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_csat = db.query(CSAT).filter(CSAT.id == csat_id).first()
    if not db_csat:
        raise HTTPException(status_code=404, detail="CSAT not found")
    update_data = csat.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_csat, field, value)
    db.commit()
    db.refresh(db_csat)
    return db_csat


@router.delete("/{csat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_csat(
    csat_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_csat = db.query(CSAT).filter(CSAT.id == csat_id).first()
    if not db_csat:
        raise HTTPException(status_code=404, detail="CSAT not found")
    db.delete(db_csat)
    db.commit()
    return None


@router.get("/stats/average", response_model=CSATAverageResponse)
def get_average_csat(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    fecha_from = datetime(year, month, 1)
    if month == 12:
        fecha_to = datetime(year + 1, 1, 1)
    else:
        fecha_to = datetime(year, month + 1, 1)

    result = (
        db.query(func.avg(CSAT.csat_score), func.count(CSAT.id))
        .filter(CSAT.fecha >= fecha_from, CSAT.fecha < fecha_to)
        .first()
    )

    if result is None:
        return CSATAverageResponse(average=0.0, total_responses=0)

    average = float(result[0]) if result[0] is not None else 0.0
    total_responses = result[1] or 0

    return CSATAverageResponse(
        average=round(average, 2),
        total_responses=total_responses,
    )


@router.get("/stats/by-agent", response_model=CSATByAgentResponse)
def get_csat_by_agent(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    fecha_from = datetime(year, month, 1)
    if month == 12:
        fecha_to = datetime(year + 1, 1, 1)
    else:
        fecha_to = datetime(year, month + 1, 1)

    csats = db.query(CSAT).filter(CSAT.fecha >= fecha_from, CSAT.fecha < fecha_to).all()

    agent_scores: dict[str, dict[str, int]] = {}
    for csat in csats:
        cesionario = csat.cesionario
        if cesionario is not None:
            agent_name = str(cesionario.name)
            if agent_name not in agent_scores:
                agent_scores[agent_name] = {"total": 0, "count": 0}
            score_val: int = csat.csat_score  # type: ignore[assignment]
            old_total = agent_scores[agent_name]["total"]
            old_count = agent_scores[agent_name]["count"]
            agent_scores[agent_name] = {
                "total": old_total + score_val,
                "count": old_count + 1,
            }

    agents_data = []
    for name, data in agent_scores.items():
        agents_data.append(
            {
                "agent": name,
                "average": round(data["total"] / data["count"], 2),
                "count": data["count"],
            }
        )

    return CSATByAgentResponse(agents=agents_data)
