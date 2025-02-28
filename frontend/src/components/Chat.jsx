import React, { useState, useEffect } from 'react';

const Chat = () => {
	const [messages, setMessages] = useState([]);
	const [inputValue, setInputValue] = useState('');
	const [socket, setSocket] = useState(null);

	useEffect(() => {
		const newSocket = new WebSocket('ws://localhost:8000/ws/141251251'); // замените 'wss://example.com/chat' на URL вашего WebSocket сервера
		setSocket(newSocket);
	}, []);

	useEffect(() => {
		if (socket) {
			socket.onopen = () => {
				console.log('WebSocket connection established.');
			};

			socket.onmessage = event => {
				const message = JSON.parse(event.data);
				setMessages(prevMessages => [...prevMessages, message]);
			};

			socket.onclose = event => {
				console.log('WebSocket connection closed:', event);
			};

			socket.onerror = error => {
				console.error('WebSocket error:', error);
			};
		}
	}, [socket]);

	const handleMessageSend = () => {
		if (inputValue.trim() === '') return;

		const message = {
			text: inputValue,
			timestamp: Date.now(),
		};

		socket.send(JSON.stringify(message));
		setInputValue('');
	};

	return (
		<div>
			<ul>
				{messages.map((message, index) => (
					<li key={index}>
						<span>{message.text}</span>
						<span>{new Date(message.timestamp).toLocaleString()}</span>
					</li>
				))}
			</ul>
			<input
				type="text"
				value={inputValue}
				onChange={e => setInputValue(e.target.value)}
			/>
			<button onClick={handleMessageSend}>Send</button>
		</div>
	);
};

export default Chat;
