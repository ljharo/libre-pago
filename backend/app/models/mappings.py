from sqlalchemy import BigInteger, Column, Integer, String

from app.database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Channel {self.name}>"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(20), default="user")

    def __repr__(self):
        return f"<Agent {self.name}>"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Team {self.name}>"
