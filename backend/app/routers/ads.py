from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import Ad
from app.schemas import AdCreate, AdResponse, AdUpdate, ChannelStatsResponse, TopCampaignStatsResponse

router = APIRouter(prefix="/api/ads", tags=["ads"])


@router.get("", response_model=list[AdResponse])
def get_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ad_adset_name: Optional[str] = None,
    ad_status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(Ad)
    if ad_adset_name:
        query = query.filter(Ad.ad_adset_name == ad_adset_name)
    if ad_status:
        query = query.filter(Ad.ad_status == ad_status)
    return query.offset(skip).limit(limit).all()


@router.get("/{ad_id}", response_model=AdResponse)
def get_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


@router.post("", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad: AdCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_ad = Ad(**ad.model_dump())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@router.put("/{ad_id}", response_model=AdResponse)
def update_ad(
    ad_id: int,
    ad: AdUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    update_data = ad.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ad, field, value)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    db_ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    db.delete(db_ad)
    db.commit()
    return None


@router.get("/stats/top-campaigns", response_model=TopCampaignStatsResponse)
def get_top_campaigns(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    fecha_from = datetime(year, month, 1)
    if month == 12:
        fecha_to = datetime(year + 1, 1, 1)
    else:
        fecha_to = datetime(year, month + 1, 1)

    ads = (
        db.query(Ad)
        .filter(
            Ad.ad_timestamp >= fecha_from,
            Ad.ad_timestamp < fecha_to,
            Ad.ad_adset_name.isnot(None),
        )
        .all()
    )

    total = len(ads)

    campaign_counts: dict[str, int] = {}
    for ad in ads:
        if ad.ad_adset_name is not None:
            adset_name = str(ad.ad_adset_name)
            campaign_counts[adset_name] = campaign_counts.get(adset_name, 0) + 1

    sorted_campaigns = sorted(campaign_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    return TopCampaignStatsResponse(
        total=total,
        campaigns=[{"campaign": k, "count": v} for k, v in sorted_campaigns],
    )


@router.get("/stats/by-channel", response_model=ChannelStatsResponse)
def get_stats_by_channel(
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

    ads = db.query(Ad).filter(Ad.ad_timestamp >= fecha_from, Ad.ad_timestamp < fecha_to).all()

    total = len(ads)

    by_channel: dict[str, int] = {}
    for ad in ads:
        channel_val: str = str(ad.ad_channel_type) if ad.ad_channel_type is not None else "Unknown"
        by_channel[channel_val] = by_channel.get(channel_val, 0) + 1

    return ChannelStatsResponse(
        total=total,
        by_channel=[{"channel": k, "count": v} for k, v in by_channel.items()],
    )
