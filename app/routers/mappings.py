from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import Agent, Channel, Team
from app.schemas import AgentCreate, AgentResponse, ChannelCreate, ChannelResponse, TeamCreate, TeamResponse

router = APIRouter(prefix="/api", tags=["mappings"])


@router.get("/channels", response_model=list[ChannelResponse])
def get_channels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return db.query(Channel).offset(skip).limit(limit).all()


@router.post("/channels", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    existing = db.query(Channel).filter(Channel.channel_id == channel.channel_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel already exists")
    db_channel = Channel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


@router.get("/agents", response_model=list[AgentResponse])
def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return db.query(Agent).offset(skip).limit(limit).all()


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    existing = db.query(Agent).filter(Agent.agent_id == agent.agent_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent already exists")
    db_agent = Agent(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.get("/teams", response_model=list[TeamResponse])
def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return db.query(Team).offset(skip).limit(limit).all()


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    existing = db.query(Team).filter(Team.team_id == team.team_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")
    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team
