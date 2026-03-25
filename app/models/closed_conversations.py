from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ClosedConversation(Base):
    __tablename__ = "closed_conversations"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False, index=True)
    contact_id = Column(Integer, nullable=False, index=True)
    nombre = Column(String(200))
    email = Column(String(200))
    telefono = Column(String(50))
    canal_id = Column(Integer, ForeignKey("channels.id"), index=True)
    cesionario_id = Column(Integer, ForeignKey("agents.id"), index=True)
    equipo_id = Column(Integer, ForeignKey("teams.id"), index=True)
    tipificacion = Column(String(200))
    resumen = Column(Text)

    canal = relationship("Channel", lazy="joined")
    cesionario = relationship("Agent", lazy="joined")
    equipo = relationship("Team", lazy="joined")

    __table_args__ = (
        Index("idx_closed_fecha_canal", "fecha", "canal_id"),
        Index("idx_closed_fecha_equipo", "fecha", "equipo_id"),
    )

    def __repr__(self):
        return f"<ClosedConversation {self.id} - {self.contact_id}>"
