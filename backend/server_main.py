import random
import time

import uvicorn
import bcrypt
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sql_app import crud, schemas, database
from sql_app .database import SessionLocal
from typing import Union
from fastapi.params import Query


app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("russian.dic", 'r', encoding='utf-8') as file:
    Dictionary = file.read().split('\n')

with open('dices.txt', 'r', encoding='utf-8') as file:
    Dices = (file.read().split('\n'))


@app.get("/in_dictionary")
async def check_word(request: Request, word: str):
    t0 = time.time()
    res = {'word': word, 'status': None}
    if word in Dictionary and word != '':
        res['status'] = True
    else:
        res['status'] = False
    t1 = time.time()
    print(t1-t0)
    return res


@app.get("/generate")
def generate_board(request: Request):
    n = 4
    random.shuffle(Dices)
    board = [[Dices[j * n + i][random.randint(0, 5)] for i in range(n)] for j in range(n)]
    result = {"board": board}
    # create_game(game=board)
    return result


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/players/")
def create_player(player: schemas.PlayerCreate):
    db = database.SessionLocal()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(player.password.encode('utf-8'), salt)
    player.password = hashed_password
    new_player = crud.create_player(db, player, salt)
    db.close()
    return new_player


@app.get("/players/{email}", response_model=Union[schemas.PlayerRead, schemas.Error])
def get_player(email: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, email)
    if db_player is None:
        return {"message": "Player not found"}
    return db_player


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/check_password/", response_model=Union[schemas.PlayerRead, schemas.Error])
def check_password(player_password: str = Query(...), email: str = Query(...), db: Session = Depends(get_db)):
    salt, password = crud.get_player_password(db, email)
    hashed_password = bcrypt.hashpw(player_password.encode('utf-8'), salt)
    if hashed_password == password:
        return {"status": True}
    else:
        return {"status": False}

# @app.post("/games/")
# def create_game(game: schemas.GameCreate):
#     db = database.SessionLocal()
#     new_game = crud.create_game(db, game)
#     db.close()
#     return {"message": "Game created successfully"}
#
#
# @app.get("/games/{game_code}", response_model=schemas.Game)
# def get_game(game_code: str, db: Session = Depends(get_db)):
#     db_game = crud.get_game(db, game_code)
#     return db_game


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
