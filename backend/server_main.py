import json
import random
import time
from ast import literal_eval
from uuid import UUID

import jwt
import os
import uvicorn
import bcrypt
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sql_app import crud, schemas, database
from sql_app .database import SessionLocal
from typing import Union, Any, List, Annotated
from fastapi.params import Query, Header, Cookie
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

app = FastAPI()
origins = [
    "http://localhost:3000",
]
database.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("russian.dic", 'r', encoding='utf-8') as file:
    Dictionary = file.read().split('\n')

with open('dices.txt', 'r', encoding='utf-8') as file:
    Dices = (file.read().split('\n'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


@app.post("/protected")
async def protected_route(request: Request):
    data = await request.json()
    refresh_token = data.get("refresh_token")
    print(refresh_token)
    # refresh_token = request.cookies.get("refresh_token")
    if refresh_token is not None:
        try:
            decoded_token = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
            if decoded_token["exp"] < time.time():
                raise HTTPException(status_code=401, detail="Refresh Token has expired")

            return {"message": "Protected Route"}
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    else:
        raise HTTPException(status_code=401, detail="Refresh Token not found")

# @app.post("/check_token/")
# def check_access_token(access_token, db: Session = Depends(get_db)):
#     try:
#         jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
#     except jwt.ExpiredSignatureError:
#         print('Token has expired')
#         try:
#             jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
#             access_token = create_access_token()
#         except jwt.ExpiredSignatureError:
#
#         return


@app.get("/in_dictionary")
async def check_word(request: Request, word: str):
    res = {'word': word, 'status': None}
    if word in Dictionary and word != '':
        res['status'] = True
    else:
        res['status'] = False
    return res


async def generate_board(access_token: str = Query(...), email: str = Query(...), db: Session = Depends(get_db)):
    n = 4
    random.shuffle(Dices)
    board = [[Dices[j * n + i][random.randint(0, 5)] for i in range(n)] for j in range(n)]
    # message = {"type": "board_update", "board": board}
    # await manager.broadcast(message)
    return board


@app.post("/register/")
def create_player(player: schemas.PlayerCreate):
    db = database.SessionLocal()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(player.password.encode('utf-8'), salt)
    player.password = hashed_password
    new_player = crud.create_player(db, player, salt)
    db.close()
    return new_player


@app.get("/authorization/{email}", response_model=Union[schemas.PlayerRead, schemas.Error])
def get_player(email: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, email)
    if db_player is None:
        return {"message": "Player not found"}
    return db_player


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_board(self, board: List[List[str]], websocket: WebSocket):
        await websocket.send_json({"type": "new_board", "board": board})

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


session_data = {}


@app.websocket("/ws/{session_id}/{access_token}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, access_token: str):
    await manager.connect(websocket)
    print(session_id, access_token)
    try:
        if not access_token:
            await websocket.close(code=1000, reason="Ввойдите в систему снова")
            return
        try:
            decoded_token = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            await websocket.close(code=1000, reason="Ввойдите в систему снова")
            return
        user_id = json.loads(decoded_token['sub'].replace("'", '"'))["user_id"]
        if session_id in session_data:
            session_data[session_id]["connections"].append((user_id, websocket))
        else:
            session_data[session_id] = {"connections": [(user_id, websocket)]}

        while True:
            data = await websocket.receive_text()
            if data == 'Connection established':
                pass
            elif data == 'Generate board':
                await manager.send_personal_board(board=await generate_board(), websocket=websocket)

    except WebSocketDisconnect:
        if session_id in session_data:
            connections = session_data[session_id]["connections"]
            user_id = next((user_id for user_id, conn in connections if conn == websocket), None)
            if user_id:
                session_data[session_id]["connections"] = [(uid, conn) for uid, conn in connections if uid != user_id]
            if len(session_data[session_id]["connections"]) == 0:
                del session_data[session_id]
        await manager.disconnect(websocket)


@app.get("/login/", response_model=Union[schemas.TokenSchema, schemas.Error])
def check_password(player_password: str = Query(...), email: str = Query(...), db: Session = Depends(get_db)):
    db_player = crud.get_player(db, email)
    salt, password = db_player.salt, db_player.password
    hashed_password = bcrypt.hashpw(player_password.encode('utf-8'), salt)
    if hashed_password == password:
        access_token = create_access_token(
            {
             "name": db_player.name,
             "matches": db_player.matches,
             "wins": db_player.wins,
             "user_id": str(db_player.id)
             }
        )
        refresh_token = create_refresh_token(
            {"user_id": db_player.id
             }
        )
        response = JSONResponse({"message": "Cookie has been set"})
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="none", secure=True, path="/", domain=".localhost", expires=int((datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).timestamp()))
        return schemas.TokenSchema(
            access_token=access_token
        )
    else:
        return schemas.Error(message="Invalid password")

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
