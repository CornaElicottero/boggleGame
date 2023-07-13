import { useState, useEffect, useRef } from 'react';
import { useCookies } from "react-cookie";
import Websocket from "react-websocket";


const Registration = () => {
	const [isValidPassword, setIsValidPassword] = useState(false);
	const className = `btn${isValidPassword ? '_highlighted' : ''}`;
	const [password, setPassword] = useState('');
	const [name, setName] = useState('');
	const [cookies, setCookie] = useCookies(['email'])
	const [isValidName, setIsValidName] = useState(false);
	const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/g;
	const email = cookies['email']
	const checkPassword = () => {
		if (isValidPassword && isValidName) {
			const createPlayer = fetch('http://localhost:8000/register/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({name: name, email: email, password: password}),
			})
				.then(response =>{
					if (response.ok){
						console.log(response.json())
					}
					else{
						console.log('Failed to create player')
					}
				})
		};
	}
	const handlePasswordChange = (e) => {
		setPassword(e.target.value);
		if (passwordRegex.test(e.target.value)) {
			setIsValidPassword(true);
		} else {
			setIsValidPassword(false);
		}
	};

	const handleNameChange = (e) => {
		setName(e.target.value);
		if(e.target.value.length !== 0){
			setIsValidName(true)
		} else{
			setIsValidName(false)
		}
	};


	return (
		<div className={"form_wrapper"}>
			<div className={"h"}>придумайте имя и&nbsp;пароль</div>
			<input className={"name_input"}
				   type="text"
				   value={name}
				   onChange={handleNameChange}
				   placeholder="имя"
			/>
			<input className={"password_input"}
				   type="password"
				   value={password}
				   onChange={handlePasswordChange}
				   placeholder="пароль"
			/>
			<div className={"smalltext"}>пароль должен содержать больше 8&nbsp;символов, минимум 1&nbsp;букву и&nbsp;1&nbsp;цифру</div>
			{isValidPassword ? (
				<div className={"status_wrapper"}>
					<div className={'valid'}></div>
					<div className={"vaild_password"}>пойдёт</div>
				</div>
			) : (
				<div className={"status_wrapper"}>
					<div className={'invalid'}></div>
					<div className={"invaild_password"}>слабый</div>
				</div>
			)}
			<button
				className={className}
				onClick={checkPassword}
			>
				создать аккаунт
			</button>
		</div>
	);
};

export default Registration;
