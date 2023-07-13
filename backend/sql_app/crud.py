import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas


def get_player(db: Session, email: str):
    return db.query(models.Player).filter(models.Player.email == email).first()


def create_player(db: Session, player: schemas.PlayerCreate, salt):
    db_player = models.Player(
        id=str(uuid.uuid4()),
        name=player.name,
        email=player.email,
        password=player.password,
        salt=salt,
        matches=0,
        wins=0)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player.__dict__


def update_player(db: Session, id: str, player_update: schemas.PlayerUpdate):
    db_player = db.query(models.Player).filter(models.Player.id == id).first()
    if db_player:
        for field, value in player_update.dict().items():
            setattr(db_player, field, value)
        db.commit()
        return True
    else:
        return False
