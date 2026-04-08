from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LifecycleBase(BaseModel):
    fecha: datetime
    contact_id: int
    ciclo_vida: str
    cesionario_id: Optional[int] = None


class LifecycleCreate(LifecycleBase):
    pass


class LifecycleUpdate(BaseModel):
    fecha: Optional[datetime] = None
    contact_id: Optional[int] = None
    ciclo_vida: Optional[str] = None
    cesionario_id: Optional[int] = None


class LifecycleResponse(LifecycleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PipelineStatsResponse(BaseModel):
    total: int
    by_stage: list[dict]
