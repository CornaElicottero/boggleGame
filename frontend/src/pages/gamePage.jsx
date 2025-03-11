import { useState, useEffect } from 'react'
import { Scoreboard, CurrentWord } from "../components/index"
import { getItem } from "../utils/encryptedLocalStorage"
import { ToastContainer, toast } from 'react-toastify'
import { useSearchParams } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'

const GamePage = () => {
	const [board, setBoard] = useState([[]])
	const [isEntered, setIsEntered] = useState([])
	const [isPressed, setIsPressed] = useState([])
	const [wordForCheck, setWordForCheck] = useState('')
	const [currentWord, setCurrentWord] = useState('')
	const [isTyping, setIsTyping] = useState(false)
	const [lastIndex, setLastIndex] = useState (0)
	const [lobbyInfo, setLobbyInfo] = useState([])
	const [accessToken, setAccessToken] = useState(getItem('access_token'))
	const [sessionId, setSessionId] = useState('')
	const [websocket, setWebsocket] = useState(null)
	const [searchParams, setSearchParams] = useSearchParams('')
	const [userID, setUserID] = useState('')
	const gameID = searchParams.get("session_id")
	const navigate = useNavigate()
	useEffect(() => {
		const CheckToken = () => {
			fetch(`http://localhost:8000/api/token/`,{
				method: 'POST',
				credentials: 'include',
				body: JSON.stringify({
					access_token: accessToken,
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
				ws.send(JSON.stringify({ action: "CONNECTION", payload: { "access_token": accessToken } }))

			};
			ws.onmessage = event => {
				const data = event.data
				const message = JSON.parse(data)
				if (message.error !== undefined) {
					toast.error(message.error, {
						position: "bottom-center",
						autoClose: 5000,
						hideProgressBar: false,
						closeOnClick: true,
						pauseOnHover: true,
						draggable: true,
						progress: undefined,
						theme: "dark",
					});
					if (message.code === 401){
						navigate("/")
					}
				} else {
					if (message["data"] !== undefined){
						setUserID(message["data"]["userID"])
						console.log(message["data"]["active_sessions"])
						if (message["data"]["active_sessions"] !== undefined && message["data"]["active_sessions"].length !== 0 ){
							ws.send(JSON.stringify({ action: "RECONNECT", payload: { "access_token": accessToken } }))
						}
						if (gameID !== null && message["data"]["active_sessions"]?.length === 0){
							ws.send(JSON.stringify({ action: "JOIN_GAME", payload: { "session_id": gameID, "access_token": accessToken }}))
						}
						if (message["data"]["session_id"] !== undefined){
							setSessionId(message["data"]["session_id"])
							setSearchParams("?session_id=" + message["data"]["session_id"])
							setBoard((message["data"]["board"]));
							setLobbyInfo(message["data"]["connections"])
						}
					}
				}
			};
			// window.onunload = function() {
			// 	if (websocket.readyState === WebSocket.OPEN) {
			// 		websocket.send(JSON.stringify({ action: "DISCONNECT", payload: "" }));
			// 	}
			// };
		}
		setupWebsocket().then()
	}, []);
	const createGameAction = () => {
		websocket.send(JSON.stringify({ action: "CREATE_GAME", payload: { "access_token": accessToken } }))
	}
	const startGameAction = () => {
		websocket.send(JSON.stringify({ action: "START_GAME", payload: {} }))
	}
	const handleMouseDown = (item, index) => {
		const updatedIsPressed = [...isPressed]
		updatedIsPressed[index] = true
		setIsPressed(updatedIsPressed)
		setIsTyping(true)
		const updatedIsEntered = [...isEntered]
		updatedIsEntered[index] = true
		setIsEntered(updatedIsEntered)
		setWordForCheck(prevWord => prevWord + item.toLowerCase())
		setLastIndex(index)
	};
	const checkWord = async ( word ) => {
		websocket.send(JSON.stringify({"action": "CHECK_WORD", "payload": { "word": word }}))
	}
	const handleWrapperMouseUp = () => {
		setIsPressed([])
		setIsEntered([])
		setCurrentWord(wordForCheck)
		checkWord(wordForCheck).then()
		setWordForCheck('')
		setIsTyping(false)

	};
	const handleWrapperMouseLeave = () => {
		setIsPressed([])
		setIsEntered([])
		setWordForCheck('')
		setIsTyping(false)
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
		)
	}
	const handleMouseEnter = (item, index) => {
		if ((isPressed[index] || isTyping) && !isEntered[index] && (Math.abs(Math.floor(index / 4) - Math.floor(lastIndex / 4)) <= 1 && Math.abs(index % 4 - lastIndex % 4) <= 1 && (Math.floor(index / 4) - Math.floor(lastIndex / 4) !== 0 || (index % 4 - lastIndex % 4) !== 0))){
			const updatedIsEntered = [...isEntered]
			updatedIsEntered[index] = true
			setIsEntered(updatedIsEntered)
			setWordForCheck(prevWord => prevWord + item.toLowerCase())
			setLastIndex(index)
		}
	}
	// const handleMouseDown = (index) => {
	//   const updatedIsPressed = [...isPressed]
	//   console.log(isPressed)
	//   updatedIsPressed[index] = true
	//   setIsPressed(updatedIsPressed)
	//   console.log(isPressed)
	// }

	return (
		<div className={"game_wrapper"}>
			<CurrentWord currentWord={wordForCheck}/>

			<Wrapper>
				{board?.flat(1)?.map((letter, letterIndex) =>
					<div className={isPressed && isEntered[letterIndex] ? 'letter_pressed' : 'letter'}
						 onMouseEnter={() => handleMouseEnter(letter, letterIndex)}
						 onMouseDown={() => handleMouseDown(letter, letterIndex)} key={letterIndex}>
						{letter}
					</div>
				)}
			</Wrapper>
			<div className={"word"}>

				{window.location.host + "/game?session_id=" + sessionId}
			</div>
			<div>
				<button onClick={() => createGameAction()}>Создать игру</button>
				<button onClick={() => startGameAction()}>Начать игру</button>
			</div>
			<Scoreboard lobbyInfo={lobbyInfo} navigate={navigate}/>
		</div>
	)
}

export default GamePage
