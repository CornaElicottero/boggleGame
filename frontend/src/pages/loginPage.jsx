import { useState } from 'react';
import { useCookies } from "react-cookie";
import { setItem } from "../utils/encryptedLocalStorage";
const LoginPage = () => {
	const [password, setPassword] = useState('');
	const [cookies, setCookie] = useCookies(['email'])
	const email = cookies['email']
	const checkEmail = () => {
		fetch(`http://localhost:8000/authorization/${email}`)
			.then(response => response.json())
			.then(data => {
				if (data.password) {
					checkPassword();
				} else {
					setCookie('email', `${email}`, {path: '/'});
					window.location.href = '/sign-up';
				}
			})
	}
	const checkPassword = () => {
		fetch(`http://localhost:8000/login/?player_password=${password}&email=${encodeURIComponent(email)}`)
			.then(response => response.json())
			.then(data => {
				if (data.access_token){
					setItem('access_token', data.access_token)
					// setCookie('refresh_token', `${data.refresh_token}`, {httpOnly: true, path: '/', sameSite: "none", domain: '.localhost'})
					window.location.href='/game'
				} else{
					alert(data.message)
				}
			})
			.catch(error => {
				console.log(error)
			});
	}
	const handlePasswordChange = (e) => {
		setPassword(e.target.value);
	};

	return (
		<div className={"form_wrapper"}>
			<div className={"h"}>введите пароль</div>
			<input className={"email_input"}
				   type="password"
				   value={password}
				   onChange={handlePasswordChange}
				   placeholder="пароль">
			</input>
			<button className={"btn_highlighted"} onClick={checkEmail}>
				далее
			</button>
		</div>
	)
}


export default LoginPage;
