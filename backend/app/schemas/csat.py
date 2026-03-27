from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CSATBase(BaseModel):
    contact_id: int
    fecha: datetime
    team_id: Optional[int] = None
    csat_score: int
    cesionario_id: Optional[int] = None
    feedback: Optional[str] = None
    tiempo_resolucion: Optional[int] = None
    tipificacion: Optional[str] = None
    resumen: Optional[str] = None


class CSATCreate(CSATBase):
    pass


class CSATUpdate(BaseModel):
    contact_id: Optional[int] = None
    fecha: Optional[datetime] = None
    team_id: Optional[int] = None
    csat_score: Optional[int] = None
    cesionario_id: Optional[int] = None
    feedback: Optional[str] = None
    tiempo_resolucion: Optional[int] = None
    tipificacion: Optional[str] = None
    resumen: Optional[str] = None


class CSATResponse(CSATBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CSATAverageResponse(BaseModel):
    average: float
    total_responses: int


class CSATByAgentResponse(BaseModel):
    agents: list[dict]
