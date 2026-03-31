from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClosedConversationBase(BaseModel):
    fecha: datetime
    contact_id: int
    canal_id: Optional[int] = None
    cesionario_id: Optional[int] = None
    equipo_id: Optional[int] = None
    tipificacion: Optional[str] = None
    resumen: Optional[str] = None


class ClosedConversationCreate(ClosedConversationBase):
    pass


class ClosedConversationUpdate(BaseModel):
    fecha: Optional[datetime] = None
    contact_id: Optional[int] = None
    canal_id: Optional[int] = None
    cesionario_id: Optional[int] = None
    equipo_id: Optional[int] = None
    tipificacion: Optional[str] = None
    resumen: Optional[str] = None


class ClosedConversationResponse(ClosedConversationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ConversationStatsResponse(BaseModel):
    total: int
    by_channel: list[dict]
    by_team: list[dict]


class AIvsHumanStatsResponse(BaseModel):
    total: int
    ai_count: int
    ai_percentage: float
    human_count: int
    human_percentage: float
