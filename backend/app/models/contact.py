from sqlalchemy import Column, Index, Integer, String

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, unique=True, nullable=False, index=True)
    nombre = Column(String(200))
    email = Column(String(200))
    telefono = Column(String(50))

    __table_args__ = (Index("idx_contact_contact_id", "contact_id"),)

    def __repr__(self):
        return f"<Contact {self.contact_id} - {self.nombre}>"
