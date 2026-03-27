from pydantic import BaseModel, ConfigDict


class ChannelBase(BaseModel):
    channel_id: int
    name: str


class ChannelCreate(ChannelBase):
    pass


class ChannelResponse(ChannelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    agent_id: int
    name: str
    agent_type: str = "user"


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TeamBase(BaseModel):
    team_id: int
    name: str


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
