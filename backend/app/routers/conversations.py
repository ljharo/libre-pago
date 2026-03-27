from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import Agent, ClosedConversation
from app.schemas import (
    AIvsHumanStatsResponse,
    ClosedConversationCreate,
    ClosedConversationResponse,
    ClosedConversationUpdate,
    ConversationStatsResponse,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ClosedConversationResponse])
def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fecha_from: Optional[datetime] = None,
    fecha_to: Optional[datetime] = None,
    canal_id: Optional[int] = None,
    equipo_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(ClosedConversation)
    if fecha_from:
        query = query.filter(ClosedConversation.fecha >= fecha_from)
    if fecha_to:
        query = query.filter(ClosedConversation.fecha <= fecha_to)
    if canal_id:
        query = query.filter(ClosedConversation.canal_id == canal_id)
    if equipo_id:
        query = query.filter(ClosedConversation.equipo_id == equipo_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{conversation_id}", response_model=ClosedConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    conversation = db.query(ClosedConversation).filter(ClosedConversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("", response_model=ClosedConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ClosedConversationCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_conversation = ClosedConversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.put("/{conversation_id}", response_model=ClosedConversationResponse)
def update_conversation(
    conversation_id: int,
    conversation: ClosedConversationUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_conversation = db.query(ClosedConversation).filter(ClosedConversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    update_data = conversation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conversation, field, value)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_conversation = db.query(ClosedConversation).filter(ClosedConversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(db_conversation)
    db.commit()
    return None


@router.get("/stats/monthly", response_model=ConversationStatsResponse)
def get_monthly_stats(
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

    conversations = (
        db.query(ClosedConversation)
        .filter(ClosedConversation.fecha >= fecha_from, ClosedConversation.fecha < fecha_to)
        .all()
    )

    total = len(conversations)

    by_channel: dict[str, int] = {}
    by_team: dict[str, int] = {}
    for c in conversations:
        if c.canal:
            channel_name = c.canal.name
            by_channel[channel_name] = by_channel.get(channel_name, 0) + 1
        if c.equipo:
            team_name = c.equipo.name
            by_team[team_name] = by_team.get(team_name, 0) + 1

    return ConversationStatsResponse(
        total=total,
        by_channel=[{"channel": k, "count": v} for k, v in by_channel.items()],
        by_team=[{"team": k, "count": v} for k, v in by_team.items()],
    )


@router.get("/stats/ai-vs-human", response_model=AIvsHumanStatsResponse)
def get_ai_vs_human_stats(
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

    ai_agent = db.query(Agent).filter(Agent.agent_type == "ai_agent").first()
    ai_agent_id = ai_agent.id if ai_agent else None

    from sqlalchemy import select

    result = db.execute(
        select(ClosedConversation.cesionario_id).where(
            ClosedConversation.fecha >= fecha_from, ClosedConversation.fecha < fecha_to
        )
    )
    cesionario_ids = [row[0] for row in result.fetchall()]
    total = len(cesionario_ids)

    if total == 0:
        return AIvsHumanStatsResponse(
            total=0,
            ai_count=0,
            ai_percentage=0.0,
            human_count=0,
            human_percentage=0.0,
        )

    ai_count = sum(1 for cid in cesionario_ids if cid == ai_agent_id)
    human_count = total - ai_count

    return AIvsHumanStatsResponse(
        total=total,
        ai_count=ai_count,
        ai_percentage=round((ai_count / total) * 100, 2),
        human_count=human_count,
        human_percentage=round((human_count / total) * 100, 2),
    )
