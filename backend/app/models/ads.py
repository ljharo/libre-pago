from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, nullable=False, index=True)
    nombre = Column(String(200))
    telefono = Column(String(50))
    agente_id = Column(Integer, ForeignKey("agents.id"), index=True)
    ad_timestamp = Column(DateTime, index=True)
    ad_channel_id = Column(String(50))
    ad_channel_type = Column(String(50))
    ad_contact_type = Column(String(50))
    ad_adset_id = Column(String(100))
    ad_adset_name = Column(String(200), index=True)
    ad_ad_url = Column(String(500))
    ad_status = Column(String(50))

    agente = relationship("Agent", lazy="joined")

    __table_args__ = (
        Index("idx_ads_timestamp", "ad_timestamp"),
        Index("idx_ads_adset_name", "ad_adset_name"),
    )

    def __repr__(self):
        return f"<Ad {self.id} - {self.contact_id}>"
