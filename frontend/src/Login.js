import React, {useState, useEffect, useRef} from 'react';
import {useCookies} from "react-cookie";


const Login = () => {
    const [password, setPassword] = useState('');
    const [cookies, setCookie] = useCookies(['email'])
    const email = cookies['email']
    const checkEmail = () => {
         fetch(`http://10.13.13.56:8000/players/${email}`)
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
        console.log(password)
        fetch(`http://10.13.13.56:8000/check_password/?player_password=${password}&email=${encodeURIComponent(email)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === true){
                    console.log(data.status)
                    console.log('Правильный пароль')
                }else{
                    console.log('Неправильный пароль')
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


export default Login;