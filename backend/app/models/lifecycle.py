from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Lifecycle(Base):
    __tablename__ = "lifecycles"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    ciclo_vida = Column(String(50), nullable=False, index=True)
    pais = Column(String(100))
    cesionario_id = Column(Integer, ForeignKey("agents.id"), index=True)
    vendedor = Column(String(200))
    canal = Column(String(50))

    contact = relationship("Contact", lazy="joined")
    cesionario = relationship("Agent", lazy="joined")

    __table_args__ = (
        Index("idx_lifecycle_contact_id", "contact_id"),
        Index("idx_lifecycle_fecha_ciclo", "fecha", "ciclo_vida"),
    )

    def __repr__(self):
        return f"<Lifecycle {self.id} - {self.contact_id} - {self.ciclo_vida}>"
