import  {useState, useEffect, useRef} from 'react';
import { Scoreboard, CurrentWord } from "./index";
import { isExpired, decodeToken } from "react-jwt";
import {useCookies} from "react-cookie";
import {getItem} from "../utils/encryptedLocalStorage";
const GenerateBoard = () => {
	const [board, setBoard] = useState([]);
	const [isEntered, setIsEntered] = useState([]);
	const [isPressed, setIsPressed] = useState([]);
	const [wordForCheck, setWordForCheck] = useState('');
	const [currentWord, setCurrentWord] = useState('')
	const [isTyping, setIsTyping] = useState(false)
	const [lastIndex, setLastIndex] = useState (0)
	const [correctWords, setCorrectWords] = useState([]);
	const [accessToken, setAccessToken] = useState(getItem('access_token'));
	const [sessionId, setSessionId] = useState('');
	const [socket, setSocket] = useState(null);
	const isFirstRender = useRef(true);
	const generateCode = () => {
		const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
		let code = '';
		for (let i = 0; i < 6; i++) {
			const randomIndex = Math.floor(Math.random() * characters.length);
			code += characters.charAt(randomIndex);
		}
		setSessionId(code)
		return code
	};
	useEffect( () => {
		if (isFirstRender.current) {
			isFirstRender.current = false;
			const CheckToken = fetch(`http://localhost:8000/protected`,{
				method: 'POST',
				credentials: 'include',
				headers: {
					'Authorization': `Bearer ${accessToken}`,
					'Content-Type': 'application/json',
					"Access-Control-Allow-Origin": "http://localhost:8000",
					"Access-Control-Allow-Headers": "http://localhost:8000",
					"Access-Control-Allow-Credentials": "http://localhost:8000"
				},
				body: JSON.stringify({
					access_token: accessToken,
					refresh_token: document.cookie.replace(/(?:(?:^|.*;\s*)refresh_token\s*\=\s*([^;]*).*$)|^.*$/, "$1")
				}),
			})
			const newSocket = new WebSocket(`ws://localhost:8000/ws/${generateCode()}/${accessToken}`);
			setSocket(newSocket);
			newSocket.onopen = event => {
				newSocket.send('Connection established');
				newSocket.send('Generate board');
			};
			newSocket.onmessage = event => {
				if (JSON.parse(event.data)["type"] === "new_board") {
					console.log(event);
					setBoard(decodeURIComponent(JSON.parse(event.data)["board"]).split(','));
				}
			};
		}
	}, []);

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

	const handleWrapperMouseUp = () => {
		setIsPressed([]);
		setIsEntered([])
		setCurrentWord(wordForCheck)
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

	const CheckWord = ({ word }) => {
		const [wordStatus, setWordStatus] = useState(null);

		useEffect(() => {
			setWordStatus(null)
			fetch(`http://localhost:8000/in_dictionary?word=${word}`,{
				method: 'GET',
				credentials: 'include',
				headers: {
					"Access-Control-Allow-Origin": "http://localhost:3000",
				}
			})
				.then(response => response.json())
				.then((data) => setWordStatus(data.status));
		}, [word]);

		useEffect(() => {
			if (wordStatus === true && !correctWords.includes(word)) {
				setCorrectWords(prevWords => [...prevWords, word]);
				// socket.send()
			}
		}, [wordStatus]);
		return (
			<>
				<div className="current">
					{wordStatus ? "Слово есть в словаре" : "Слова нет в словаре"}
				</div>
			</>
		);
	};

	return (
		<div className={"game_wrapper"}>
			<CheckWord word={currentWord} />
			<CurrentWord currentWord={wordForCheck} />
			<Wrapper>
				{board.map((item, index) => (
					<div
						className={`letter${isPressed && isEntered[index] ? '_pressed' : ''}`}
						onMouseEnter={() => handleMouseEnter(item, index)}
						onMouseDown={() => handleMouseDown(item, index)}
						key={index}
					>
						{item}
					</div>
				))}
			</Wrapper>
			<Scoreboard correctWords={correctWords}/>
		</div>
	);
};

export default GenerateBoard;
