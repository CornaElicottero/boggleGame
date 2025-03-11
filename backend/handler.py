from typing import List

from fastapi import WebSocket
import jwt
import asyncio

from config import SECRET_KEY, ALGORITHM
from token_utils import check_token
from connection_manager import manager
from status import update_status
from session_code_generator import generate_session_code
from generate_board import generate_board
from check_word import check_word


class ActionHandler:
    active_sessions = [{
        "session_id": str,
        "game_state": False,
        "board": List[List[str]],
        "connections": [
            {
                "username": str,
                "user_id": str,
                "websocket": WebSocket,
                "words": List[str],
                "player_status": True
            }
        ],
        "websockets": [],
        "words": [],
    }]
    reconnect_timers = {}
    def update_status(self, data) -> str:
        return update_status(data)

    async def get_parameter_from_access_token(self, access_token, parameter, websocket: WebSocket):
        try:
            decoded_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            user_id = decoded_token[parameter]
            return user_id
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            await self.send_personal_error_message("Unauthorized", 401, websocket)

    def get_user_id_from_websocket(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        if not session:
            return
        connections = session["connections"]
        connection = next((connection for connection in connections
                           if connection["websocket"] == websocket), None)
        user_id = connection["user_id"]
        return user_id

    def get_word_list_from_websocket(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        if not session:
            return
        connections = session["connections"]
        connection = next((connection for connection in connections if connection["websocket"] == websocket), None)
        words = connection["words"]
        return words

    async def send_personal_error_message(self, message, code, websocket: WebSocket):
        await manager.send_personal_message(f'{{"error":"{message}", "code":{code}}}', websocket)

    def get_session_from_user_id(self, user_id):
        return next((session for session in self.active_sessions
                        if any(connection['user_id'] == user_id for connection in session['connections'])), None)

    def get_session_by_websocket(self, websocket: WebSocket):
        return next((session for session in self.active_sessions
                        if any(connection['websocket'] == websocket for connection in session['connections'])), None)

    def get_session_for_send(self, session):
        session_for_send = {
            key: value for key, value in session.items() if key != "websockets"
        }
        session_for_send["connections"] = [
            {key: value for key, value in connections.items() if key != "websocket"}
            for connections in session["connections"]
        ]
        return session_for_send
    async def handle_connect_action(self, access_token, websocket: WebSocket):
        active_sessions = []
        user_id = await self.get_parameter_from_access_token(access_token=access_token,
                                                       parameter="user_id", websocket=websocket)
        username = await self.get_parameter_from_access_token(access_token=access_token,
                                                        parameter="username", websocket=websocket)
        session = self.get_session_from_user_id(user_id)
        if session is not None:
            active_sessions.append(self.get_session_for_send(session))
        await manager.send_personal_message(
            self.update_status({
                "username": username,
                "user_id": user_id,
                "active_sessions": active_sessions
            }),
            websocket
        )

    async def handle_disconnect_action(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        if not session:
            return
        connections = session["connections"]
        if any(connection["websocket"] == websocket for connection in connections):
            connection = next((connection for connection in connections if connection["websocket"] == websocket), None)
            connection["player_status"] = False
            session["websockets"].remove(websocket)
            session["game_state"] = False
            # session["connections"] = [connection for connection in connections if connection["websocket"] != websocket]
            # self.session["connections"] = session["connections"]
        if len(session["websockets"]) == 0:
            self.active_sessions.remove(session)
        self.reconnect_timers[session["session_id"]] = asyncio.create_task(self.wait_for_reconnect(session, session["session_id"]))
        await manager.send_session_message(
            self.update_status({
                "type": "player_disconnected",
                "timer": 60
            }),
            session["websockets"]
        )
        await manager.send_session_message(
            self.update_status(self.get_session_for_send(session)),
            session["websockets"]
        )

    async def handle_reconnect_action(self, access_token, websocket: WebSocket):
        user_id = await self.get_parameter_from_access_token(access_token, "user_id", websocket)
        session = self.get_session_from_user_id(user_id)
        if not session:
            await self.send_personal_error_message("Сессия к которой вы пытаетесь переподключиться больше не существует", 404, websocket)
            return
        if session["session_id"] in self.reconnect_timers:
            self.reconnect_timers[session["session_id"]].cancel()
            del self.reconnect_timers[session["session_id"]]
            session["websockets"].append(websocket)
            connections = session["connections"]
            connection = next((connection for connection in connections if connection["user_id"] == user_id), None)
            connection["websocket"] = websocket
            connection["player_status"] = True
            session["game_state"] = True
            await manager.send_session_message(
                self.update_status({"type": "player_reconnected"}),
                session["websockets"]
            )
            await manager.send_session_message(
                self.update_status(self.get_session_for_send(session)),
                session["websockets"]
            )


    async def wait_for_reconnect(self, session, session_id):
        await asyncio.sleep(60)
        if session in self.active_sessions:
            await manager.send_session_message(
                self.update_status({"type": "delete_session"}),
                session["websockets"]
            )
            self.active_sessions.remove(session)
            del self.reconnect_timers[session_id]



    async def create_game_action(self, session_id, access_token, websocket: WebSocket):
        user_id, username = (await self.get_parameter_from_access_token(access_token, "user_id", websocket),
                             await self.get_parameter_from_access_token(access_token, "username", websocket))
        self.active_sessions.append(
            {"session_id": session_id, "websockets": [websocket], "words": [],
             "connections": [{"user_id": user_id, "username": username, "words": [], "websocket": websocket, "player_status": True}]})
        session = self.get_session_by_websocket(websocket)
        await manager.send_session_message(
            self.update_status(self.get_session_for_send(session)),
            session["websockets"]
        )

    async def start_game_action(self, websocket: WebSocket):
        session = self.get_session_by_websocket(websocket)
        if len(session["websockets"]) == 2:
            board = generate_board()
            session["board"] = board
            session["game_state"] = True
            await manager.send_session_message(
                self.update_status(self.get_session_for_send(session)),
                session["websockets"]
            )
        else:
            await self.send_personal_error_message("Ожидание подключения второго игрока", 400, websocket)

    async def join_game_action(self, session_id, access_token, websocket: WebSocket):
        user_id = await self.get_parameter_from_access_token(access_token=access_token,
                                                       parameter="user_id", websocket=websocket)
        username = await self.get_parameter_from_access_token(access_token=access_token,
                                                        parameter="username", websocket=websocket)
        if any(session["session_id"] == session_id for session in self.active_sessions):
            for session in self.active_sessions:
                if session['session_id'] == session_id:
                    session["connections"].append(
                        {"user_id": user_id, "username": username, "words": [], "websocket": websocket, "player_status": True})
                    session["websockets"].append(websocket)
                    break
            session = self.get_session_by_websocket(websocket)
            await manager.send_session_message(
                self.update_status(self.get_session_for_send(session)),
                session["websockets"]
            )
        else:
            await self.send_personal_error_message("Такой комнаты несуществует", 404, websocket)

    async def check_word_action(self, word, websocket: WebSocket):
        websockets = self.get_session_by_websocket(websocket)["websockets"]
        word_status = check_word(word)
        user_id = self.get_user_id_from_websocket(websocket)
        word_list = self.get_session_by_websocket(websocket)["words"]
        if len(word) < 3:
            await self.send_personal_error_message("Слишком короткое слово", 0, websocket)
            return
        if not word_status:
            await self.send_personal_error_message("Такого слова нет в словаре", 0, websocket)
            return
        if word not in word_list:
            session = self.get_session_by_websocket(websocket)
            session["words"].append(word)
            connection = next((connection for connection in session["connections"]
                               if connection["user_id"] == user_id), None)
            connection["words"].append(word)
            await manager.send_session_message(
                self.update_status(self.get_session_for_send(session)),
                websockets
            )
        else:
            await self.send_personal_error_message("Слово уже найдено", 0, websocket)

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
                await self.handle_connect_action(access_token=payload["access_token"], websocket=websocket)
            case 'CREATE_GAME':
                await self.create_game_action(session_id=generate_session_code(), access_token=payload["access_token"], websocket=websocket)
            case 'START_GAME':
                await self.start_game_action(websocket=websocket)
            case 'JOIN_GAME':
                await self.join_game_action(session_id=payload["session_id"],
                                            access_token=payload["access_token"], websocket=websocket)
            case 'CHECK_WORD':
                await self.check_word_action(word=payload["word"], websocket=websocket)
            case 'DISCONNECT':
                await self.handle_disconnect_action(websocket=websocket)
            case 'RECONNECT':
                await self.handle_reconnect_action(access_token=payload["access_token"], websocket=websocket)
            case '_':
                await self.send_personal_error_message("Bad Request", 400, websocket)


handler = ActionHandler()
