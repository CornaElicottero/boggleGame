import React from 'react';
import ReactDOM from 'react-dom';
import {
    BrowserRouter,
    Route,
    Routes,
    useParams
} from 'react-router-dom';
import { createRoot } from 'react-dom';
import App from './GenerateBoard';
import Scoreboard from './Scoreboard';
import './index.css';
import Auth from "./Authorization";
import Reg from "./Registration";
import Login from "./Login";

const AppFull = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/game" element={<App />} />
        <Route path="/sign-up" element={<Reg/>} />
        <Route path="/" element={<Auth/>} />
        <Route path="/login" element={<Login />}/>
      </Routes>
    </BrowserRouter>
  );
};

ReactDOM.render(<AppFull />, document.getElementById('root'));
