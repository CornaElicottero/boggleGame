import uuid
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from .database import Base


class Player(Base):
    __tablename__ = "player"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, index=True)
    name = Column(String, index=True)
    password = Column(BYTEA, index=True)
    salt = Column(BYTEA, index=True)
    matches = Column(Integer, index=True)
    wins = Column(Integer, index=True)

