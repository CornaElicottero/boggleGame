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
from typing import Union, Any, List, Annotated
from fastapi.params import Query, Header, Cookie
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from dotenv import load_dotenv

from db import schemas, database, crud
from db .database import SessionLocal
from connection_manager import manager
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from token_utils import create_token
from handler import handler

load_dotenv()

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




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/token/")
async def protected_route(request: Request):
    data = await request.json()
    access_token = data.get("access_token")
    # refresh_token = request.cookies.get("refresh_token")
    if access_token is not None:
        try:
            decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            if decoded_token["exp"] < time.time():
                raise HTTPException(status_code=401, detail="Access Token has expired")

            return {"message": "Protected Route"}
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Access Token")
    else:
        raise HTTPException(status_code=401, detail="Access Token not found")

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


# @app.get("/api/checkWord")
# async def check_word(request: Request, word: str):
#     res = {'word': word, 'status': None}
#     if word in Dictionary and word != '':
#         res['status'] = True
#     else:
#         res['status'] = False
#     return res

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


@app.websocket("/api/ws/")
async def websocket_endpoint(
        websocket: WebSocket,
        db: Session = Depends(get_db)
):
    await manager.connect(websocket)
    try:

    # try:
    #     decoded_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
    #     user_id = decoded_token["user_id"]
        # user_id = json.loads(decoded_token['sub'].replace("'", '"'))["user_id"]
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                await handler.handle(
                    action=data["action"],
                    payload=data["payload"],
                    websocket=websocket,
                )
            except json.JSONDecodeError:
                print("Decoding Error")
                continue
    except WebSocketDisconnect:
        await handler.handle_disconnect_action(websocket)
    # except (jwt.ExpiredSignatureError, jwt.DecodeError):
    #     handler.handle_disconnect_action(session_id)
    #     manager.disconnect(websocket)


@app.get("/login/", response_model=Union[schemas.TokenSchema, schemas.Error])
def check_password(player_password: str = Query(...), email: str = Query(...), db: Session = Depends(get_db)):
    db_player = crud.get_player(db, email)
    salt, password = db_player.salt, db_player.password
    hashed_password = bcrypt.hashpw(player_password.encode('utf-8'), salt)
    if hashed_password == password:
        access_token = create_token(
            {
             "username": db_player.name,
             "matches": db_player.matches,
             "wins": db_player.wins,
             "user_id": str(db_player.id)
             }
        )
        # refresh_token = create_refresh_token(
        #     {"user_id": db_player.id
        #      }
        # )
        # response = JSONResponse({"message": "Cookie has been set"})
        # response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="none", secure=True, path="/", domain=".localhost", expires=int((datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).timestamp()))
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
