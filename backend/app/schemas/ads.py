from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AdBase(BaseModel):
    contact_id: int
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    agente_id: Optional[int] = None
    ad_timestamp: Optional[datetime] = None
    ad_channel_id: Optional[str] = None
    ad_channel_type: Optional[str] = None
    ad_contact_type: Optional[str] = None
    ad_adset_id: Optional[str] = None
    ad_adset_name: Optional[str] = None
    ad_ad_url: Optional[str] = None
    ad_status: Optional[str] = None


class AdCreate(AdBase):
    pass


class AdUpdate(BaseModel):
    contact_id: Optional[int] = None
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    agente_id: Optional[int] = None
    ad_timestamp: Optional[datetime] = None
    ad_channel_id: Optional[str] = None
    ad_channel_type: Optional[str] = None
    ad_contact_type: Optional[str] = None
    ad_adset_id: Optional[str] = None
    ad_adset_name: Optional[str] = None
    ad_ad_url: Optional[str] = None
    ad_status: Optional[str] = None


class AdResponse(AdBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TopCampaignStatsResponse(BaseModel):
    total: int
    campaigns: list[dict]


class ChannelStatsResponse(BaseModel):
    total: int
    by_channel: list[dict]
