from typing import List

from sqlalchemy.orm import Session
from fastapi import WebSocket
import jwt

from config import SECRET_KEY, ALGORITHM
from token_utils import check_token
from connection_manager import manager
from status import update_status
from session_code_generator import generate_session_code
from generate_board import generate_board
from check_word import check_word


class ActionHandler:
    session = {
        "session_id": str,
        "game_state": False,
        "board": List[List[str]],
        "connections": [
            {
                "username": str,
                "user_id": str,
                "words": List[str]
            }
        ]
    }
    active_sessions = [{
        "session_id": str,
        "game_state": False,
        "board": List[List[str]],
        "connections": [
            {
                "username": str,
                "user_id": str,
                "websocket": WebSocket,
                "words": List[str]
            }
        ],
        "websockets": [],
        "words": [],
    }]

    def update_status(self) -> str:
        return update_status(self.session)

    # def admin_update_status(self, access_token, refresh_token) -> str:
    #     return json.dumps(
    #         {
    #             "queue": self.queue,
    #             "history": self.history,
    #             "play_count": self.play_count,
    #             "live": self.live,
    #             "is_admin": True,
    #             "access_token": access_token,
    #             "refresh_token": refresh_token
    #         }
    #     )

    def get_parameter_from_access_token(self, access_token, parameter, websocket: WebSocket):
        try:
            decoded_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            user_id = decoded_token[parameter]
            return user_id
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            manager.disconnect(websocket)

    def get_user_id_from_websocket(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        connections = session["connections"]
        connection = next((connection for connection in connections
                           if connection["websocket"] == websocket), None)
        user_id = connection["user_id"]
        return user_id

    def get_word_list_from_websocket(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        connections = session["connections"]
        connection = next((connection for connection in connections if connection["websocket"] == websocket), None)
        words = connection["words"]
        return words

    async def send_personal_error_message(self, message, websocket: WebSocket):
        await manager.send_personal_message(f'{{"error":"{message}"}}', websocket)

    def get_session_by_websocket(self, websocket: WebSocket):
        session = next((session for session in self.active_sessions
                        if any(connection['websocket'] == websocket for connection in session['connections'])), None)
        if session is not None:
            return session

    async def handle_connection_action(self, session_id, access_token, websocket: WebSocket):
        user_id = self.get_parameter_from_access_token(access_token=access_token,
                                                       parameter="user_id", websocket=websocket)
        username = self.get_parameter_from_access_token(access_token=access_token,
                                                        parameter="username", websocket=websocket)
        self.active_sessions.append(
            {"session_id": session_id, "websockets": [websocket], "words": [],
             "connections": [{"user_id": user_id, "username": username, "words": [], "websocket": websocket}]})
        self.session = {"session_id": session_id, "connections": [{"user_id": user_id,
                                                                   "username": username, "words": []}]}
        await manager.send_personal_message(
            self.update_status(),
            websocket
        )

    async def handle_disconnect_action(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        connections = session["connections"]
        if any(connection["websocket"] == websocket for connection in connections):
            session["connections"] = [connection for connection in connections if connection["websocket"] != websocket]
            self.session["connections"] = session["connections"]
        if len(session["connections"]) == 0:
            self.active_sessions.remove(session)
        await manager.send_session_message(
            self.update_status(),
            self.session["websockets"]
        )

    async def start_game_action(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        board = generate_board()
        session["board"] = board
        self.session["board"] = board
        await manager.send_personal_message(
            self.update_status(),
            websocket
        )

    async def join_game_action(self, session_id, access_token, websocket: WebSocket):
        user_id = self.get_parameter_from_access_token(access_token=access_token,
                                                       parameter="user_id", websocket=websocket)
        username = self.get_parameter_from_access_token(access_token=access_token,
                                                        parameter="username", websocket=websocket)
        if any(session["session_id"] == session_id for session in self.active_sessions):
            for session in self.active_sessions:
                if session['session_id'] == session_id:
                    session["connections"].append(
                        {"user_id": user_id, "username": username, "words": [], "websocket": websocket})
                    session["websockets"].append(websocket)
                    self.session["connections"].append({"user_id": user_id, "username": username, "words": []})
                    break
            await manager.send_session_message(
                self.update_status(),
                self.get_session_by_websocket(websocket)["websockets"]
            )
        else:
            await self.send_personal_error_message("Такой комнаты несуществует", websocket)
            manager.disconnect(websocket)

    async def check_word_action(self, word, websocket: WebSocket):
        websockets = self.get_session_by_websocket(websocket)["websockets"]
        word_status = check_word(word)
        user_id = self.get_user_id_from_websocket(websocket)
        word_list = self.get_session_by_websocket(websocket)["words"]
        if len(word) < 3:
            await self.send_personal_error_message("Слишком короткое слово", websocket)
            return
        if not word_status:
            await self.send_personal_error_message("Такого слова нет в словаре", websocket)
            return
        if word not in word_list:
            self.get_session_by_websocket(websocket)["words"].append(word)
            connection = next((connection for connection in self.session["connections"]
                               if connection["user_id"] == user_id), None)
            connection["words"].append(word)
            await manager.send_session_message(
                self.update_status(),
                websockets
            )
        else:
            await self.send_personal_error_message("Слово уже найдено", websocket)

    # async def handle_start_stream_action(self, access_token, refresh_token, websocket: WebSocket):
    #     access_token, refresh_token = check_token(access_token, refresh_token)
    #     if access_token is None or refresh_token is None:
    #         await self.send_personal_error_message("Недостаточно прав", websocket)
    #         return
    #
    #     self.live = True
    #     self.queue = []
    #     self.history = []
    #     self.play_count = []
    #
    #     await manager.send_personal_message(self.admin_update_status(access_token, refresh_token), websocket)
    #     await manager.broadcast(self.update_status())
    #
    # async def handle_end_stream_action(self, access_token, refresh_token, websocket: WebSocket):
    #     access_token, refresh_token = check_token(access_token, refresh_token)
    #     if access_token is None or refresh_token is None:
    #         await self.send_personal_error_message("Недостаточно прав", websocket)
    #         return
    #
    #     self.live = False
    #     self.queue = []
    #     self.play_count = []
    #
    #     await manager.send_personal_message(self.admin_update_status(access_token, refresh_token), websocket)
    #     await manager.broadcast(self.update_status())
    #
    # async def handle_add_song_action(self, db: Session, song_id, client_id, websocket: WebSocket):
    #     new_song = CRUD.get_song_by_id(db, song_id)
    #     if not self.live:
    #         await self.send_personal_error_message("Стрим оффлайн", websocket)
    #         return
    #
    #     if any(song["song_id"] == new_song.id for song in self.queue):
    #         await self.send_personal_error_message("Уже в очереди", websocket)
    #         return
    #
    #     songs_by_client = [song for song in self.queue if song["client_id"] == client_id]
    #     if len(songs_by_client) == MAX_SONGS_COUNT:
    #         await self.send_personal_error_message("Вы добавили максимальное количество песен", websocket)
    #         return
    #
    #     found_song = next((song for song in self.play_count if song["song_id"] == new_song.id), None)
    #     if found_song is not None:
    #         if found_song[0]["count"] == 2:
    #             await self.send_personal_error_message("Эта песня дважды сыграла на стриме", websocket)
    #             return
    #
    #         found_song[0]["count"] += 1
    #     else:
    #         self.play_count.append({
    #             "song_id": new_song.id,
    #             "count": 1
    #         })
    #
    #     self.queue.append({
    #         "song_id": new_song.id,
    #         "artist": new_song.artist,
    #         "song": new_song.song,
    #         "client_id": client_id
    #     })
    #
    #     await manager.broadcast(self.update_status())
    #
    # async def handle_move_to_history_action(self, access_token, refresh_token, websocket: WebSocket):
    #     access_token, refresh_token = check_token(access_token, refresh_token)
    #     if access_token is None or refresh_token is None:
    #         await self.send_personal_error_message("Недостаточно прав", websocket)
    #         return
    #
    #     if self.queue:
    #         self.history.append(self.queue.pop(0))
    #
    #     await manager.send_personal_message(self.admin_update_status(access_token, refresh_token), websocket)
    #     await manager.broadcast(self.update_status())
    #
    # async def handle_return_from_history_action(self, access_token, refresh_token, websocket: WebSocket):
    #     access_token, refresh_token = check_token(access_token, refresh_token)
    #     if access_token is None or refresh_token is None:
    #         await self.send_personal_error_message("Недостаточно прав", websocket)
    #         return
    #
    #     if self.history:
    #         self.queue.insert(0, self.history.pop(-1))
    #
    #     await manager.send_personal_message(self.admin_update_status(access_token, refresh_token), websocket)
    #     await manager.broadcast(self.update_status())
    #
    # async def handle_delete_song_action(self, song_id):
    #     self.queue = [song for song in self.queue if not song['song_id'] == song_id]
    #     found_song = [song for song in self.play_count if song["song_id"] == song_id]
    #     if found_song:
    #         found_song[0]["count"] -= 1
    #         if found_song[0]["count"] <= 0:
    #             self.play_count = [song for song in self.play_count if not song['song_id'] == song_id]
    #     await manager.broadcast(self.update_status())

    async def handle(
            self,
            action: str,
            payload: dict,
            websocket: WebSocket,
    ):
        match action:
            case 'CONNECTION':
                await self.handle_connection_action(session_id=generate_session_code(),
                                                    access_token=payload["access_token"], websocket=websocket)
            case 'START_GAME':
                await self.start_game_action(websocket=websocket)
            case 'JOIN_GAME':
                await self.join_game_action(session_id=payload["session_id"],
                                            access_token=payload["access_token"], websocket=websocket)
            case 'CHECK_WORD':
                await self.check_word_action(word=payload["word"], websocket=websocket)
            # case 'START_STREAM':
            #     await self.handle_start_stream_action(payload["access_token"], payload["refresh_token"], websocket)
            # case 'END_STREAM':
            #     await self.handle_end_stream_action(payload["access_token"], payload["refresh_token"], websocket)
            # case 'ADD_SONG':
            #     await self.handle_add_song_action(db, payload["song_id"], client_id, websocket)
            # case 'MOVE_TO_HISTORY':
            #     await self.handle_move_to_history_action(payload["access_token"], payload["refresh_token"], websocket)
            # case 'RETURN_FROM_HISTORY':
            #     await self.handle_return_from_history_action(payload["access_token"], payload["refresh_token"], websocket)
            # case 'DELETE_SONG':
            #     await self.handle_delete_song_action(payload["song_id"])


handler = ActionHandler()
