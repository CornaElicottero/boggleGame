import { useState, useEffect, useRef } from 'react';
import {Scoreboard, CurrentWord, WordStatus} from "../components/index";
import { getItem } from "../utils/encryptedLocalStorage";
import { ToastContainer, toast } from 'react-toastify';
import { useSearchParams } from 'react-router-dom'

const GamePage = () => {
	const [board, setBoard] = useState([[]])
	const [isEntered, setIsEntered] = useState([])
	const [isPressed, setIsPressed] = useState([])
	const [wordForCheck, setWordForCheck] = useState('')
	const [currentWord, setCurrentWord] = useState('')
	const [isTyping, setIsTyping] = useState(false)
	const [lastIndex, setLastIndex] = useState (0)
	const [playerInfo, setPlayerInfo] = useState([])
	const [accessToken, setAccessToken] = useState(getItem('access_token'))
	const [sessionId, setSessionId] = useState('')
	const [websocket, setWebsocket] = useState(null)
	const [searchParams, setSearchParams] = useSearchParams('');
	const search = searchParams.get("session_id")
	useEffect(() => {
		const CheckToken = () => {
			fetch(`http://localhost:8000/api/token/`,{
				method: 'POST',
				credentials: 'include',
				// headers: {
				// 	'Authorization': `Bearer ${accessToken}`,
				// 	'Content-Type': 'application/json',
				// 	"Access-Control-Allow-Origin": "http://localhost:8000",
				// 	"Access-Control-Allow-Headers": "http://localhost:8000",
				// 	"Access-Control-Allow-Credentials": "http://localhost:8000"
				// },
				body: JSON.stringify({
					access_token: accessToken,
					// refresh_token: document.cookie.replace(/(?:(?:^|.*;\s*)refresh_token\s*\=\s*([^;]*).*$)|^.*$/, "$1")
				})
			})
				.then(response => response.json())
				.then(data => console.log(data))
		}
		CheckToken()
	}, []);
	useEffect( () => {
		const setupWebsocket = async () => {
			const websocketURL = 'ws://localhost:8000/api/ws/'
			const ws = new WebSocket(websocketURL);
			setWebsocket(ws)
			ws.onopen = event => {
				if (search !== null){
					ws.send(JSON.stringify({ action: "JOIN_GAME", payload: { "session_id": search, "access_token": accessToken }}))
				}
				else {
					ws.send(JSON.stringify({ action: "CONNECTION", payload: { "access_token": accessToken }}))
					ws.send(JSON.stringify({ action: "START_GAME", payload: "" }))
				}

			};
			ws.onmessage = event => {
				const message = event.data
				if (JSON.parse(message).error !== undefined) {
					toast.error(JSON.parse(message).error, {
						position: "bottom-center",
						autoClose: 5000,
						hideProgressBar: false,
						closeOnClick: true,
						pauseOnHover: true,
						draggable: true,
						progress: undefined,
						theme: "dark",
					});
				} else {
					if (JSON.parse(message)["session"]["session_id"] !== undefined){
						// setSessionId(JSON.parse(message)["session"]["session_id"])
						setBoard((JSON.parse(message)["session"]["board"]));
						console.log(JSON.parse(message)["session"]["connections"])
						setPlayerInfo(JSON.parse(message)["session"]["connections"])
					}
				}
			};
			window.onbeforeunload = function() {
				websocket.onclose = function () {
					websocket.send(JSON.stringify({ action: "DISCONNECT", payload: "" }))
				};
			};
		}
		setupWebsocket().then()
	}, [sessionId]);

	const handleMouseDown = (item, index) => {
		const updatedIsPressed = [...isPressed]
		updatedIsPressed[index] = true;
		setIsPressed(updatedIsPressed);
		setIsTyping(true)
		const updatedIsEntered = [...isEntered];
		updatedIsEntered[index] = true;
		setIsEntered(updatedIsEntered);
		setWordForCheck(prevWord => prevWord + item.toLowerCase())
		setLastIndex(index)
	};
	const checkWord = async ( word ) => {
		websocket.send(JSON.stringify({"action": "CHECK_WORD", "payload": { "word": word }}))
	}
	const handleWrapperMouseUp = () => {
		setIsPressed([]);
		setIsEntered([])
		setCurrentWord(wordForCheck)
		checkWord(wordForCheck).then()
		setWordForCheck('')
		setIsTyping(false)

	};
	const handleWrapperMouseLeave = () => {
		setIsPressed([]);
		setIsEntered([]);
		setWordForCheck('');
		setIsTyping(false);
	}
	const Wrapper = ({ children }) => {
		return (
			<div
				className="wrapper"
				onMouseUp={handleWrapperMouseUp}
				onMouseLeave={handleWrapperMouseLeave}
			>
				{children}
			</div>
		);
	};
	const handleMouseEnter = (item, index) => {
		if ((isPressed[index] || isTyping) && !isEntered[index] && (Math.abs(Math.floor(index / 4) - Math.floor(lastIndex / 4)) <= 1 && Math.abs(index % 4 - lastIndex % 4) <= 1 && (Math.floor(index / 4) - Math.floor(lastIndex / 4) !== 0 || (index % 4 - lastIndex % 4) !== 0))){
			const updatedIsEntered = [...isEntered];
			updatedIsEntered[index] = true;
			setIsEntered(updatedIsEntered);
			setWordForCheck(prevWord => prevWord + item.toLowerCase())
			setLastIndex(index)
		}
	}
	// const handleMouseDown = (index) => {
	//   const updatedIsPressed = [...isPressed]
	//   console.log(isPressed)
	//   updatedIsPressed[index] = true;
	//   setIsPressed(updatedIsPressed)
	//   console.log(isPressed)
	// }

	return (
		<div className={"game_wrapper"}>
			{/*<WordStatus word={currentWord} ws={websocket} />*/}
			<CurrentWord currentWord={wordForCheck} />
			<Wrapper>
				{board?.flat(1)?.map((letter, letterIndex) =>
					<div className={isPressed && isEntered[letterIndex] ? 'letter_pressed' : 'letter'} onMouseEnter={() => handleMouseEnter(letter, letterIndex)} onMouseDown={() => handleMouseDown(letter, letterIndex)} key={letterIndex}>
						{letter}
					</div>
					)}
			</Wrapper>
			<Scoreboard playerInfo={playerInfo}/>
			<ToastContainer
				position="bottom-center"
				autoClose={5000}
				hideProgressBar={false}
				newestOnTop
				closeOnClick
				rtl={false}
				pauseOnFocusLoss
				draggable
				pauseOnHover
				theme="dark"
			/>
		</div>
	);
};

export default GamePage;
