from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CSAT(Base):
    __tablename__ = "csat"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    fecha = Column(DateTime, nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    canal_id = Column(Integer, ForeignKey("channels.id"), index=True)
    csat_score = Column(Integer, nullable=False)
    cesionario_id = Column(Integer, ForeignKey("agents.id"), index=True)
    feedback = Column(Text)
    tiempo_resolucion = Column(Integer)
    tipificacion = Column(String(200))
    resumen = Column(Text)

    contact = relationship("Contact", lazy="joined")
    team = relationship("Team", lazy="joined")
    cesionario = relationship("Agent", lazy="joined")

    __table_args__ = (
        Index("idx_csat_fecha", "fecha"),
        Index("idx_csat_agent", "cesionario_id"),
    )

    def __repr__(self):
        return f"<CSAT {self.id} - {self.contact_id}>"
