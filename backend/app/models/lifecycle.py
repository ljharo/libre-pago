from sqlalchemy import Column, DateTime, Index, Integer, String

from app.database import Base


class Lifecycle(Base):
    __tablename__ = "lifecycles"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False, index=True)
    contact_id = Column(Integer, nullable=False, index=True)
    ciclo_vida = Column(String(50), nullable=False, index=True)
    nombre = Column(String(200))
    email = Column(String(200))
    telefono = Column(String(50))
    pais = Column(String(100))
    cesionario = Column(String(200))
    vendedor = Column(String(200))
    canal = Column(String(50))

    __table_args__ = (
        Index("idx_lifecycle_contact_id", "contact_id"),
        Index("idx_lifecycle_fecha_ciclo", "fecha", "ciclo_vida"),
    )

    def __repr__(self):
        return f"<Lifecycle {self.id} - {self.contact_id} - {self.ciclo_vida}>"
