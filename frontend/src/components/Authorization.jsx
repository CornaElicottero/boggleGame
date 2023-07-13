import {useState, useEffect} from "react";
import { Link, useParams } from 'react-router-dom';
import { useCookies } from 'react-cookie';
import Websocket from "react-websocket";


const Authorization = () => {
	const [isValidEmail, setIsValidEmail] = useState(false);
	const [email, setEmail] = useState('');
	const [cookies, setCookie] = useCookies(['email'])
	const emailRegex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}/g;
	const handleEmailChange = (e) => {
		setEmail(e.target.value);
		setIsValidEmail(emailRegex.test(e.target.value));
	};

	const checkEmail = () => {
		if (isValidEmail) {
			fetch(`http://localhost:8000/authorization/${email}`)
				.then(response => response.json())
				.then(data => {
					if (data.password) {
						setCookie('email', `${email}`, {path: '/'});
						window.location.href = '/login';
					} else {
						setCookie('email', `${email}`, {path: '/'})
						window.location.href = '/sign-up';
					}
				})
		}
	}
	return (
		<div className="form_wrapper">
			<div className="h">введите email</div>
			<input
				className="email_input"
				type="text"
				value={email}
				onChange={handleEmailChange}
				placeholder="Email"
			/>
			<button className={`btn${isValidEmail ? '_highlighted' : ''}`} onClick={checkEmail}>
				далее
			</button>
		</div>
	);
};


export default Authorization;
