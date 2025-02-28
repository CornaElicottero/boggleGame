import uuid
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID, BYTEA, VARCHAR
from .database import Base


class Player(Base):
    __tablename__ = "player"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(VARCHAR, index=True)
    name = Column(VARCHAR, index=True)
    password = Column(BYTEA, index=True)
    salt = Column(BYTEA, index=True)
    matches = Column(Integer, index=True)
    wins = Column(Integer, index=True)


# class Game(Base):
#     _tablename_ = "games"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)