import { useState } from "react";
import { useCookies } from 'react-cookie';


const MainPage = () => {
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
					setCookie('email', `${email}`, {path: '/'});
					if (data.password) {
						window.location.href = '/login';
					} else {
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
				placeholder="email"
			/>
			<button className={isValidEmail ? 'btn_highlighted': 'btn'} onClick={checkEmail}>
				далее
			</button>
		</div>
	);
};


export default MainPage;
