import { BrowserRouter, Route, Routes, useParams } from 'react-router-dom';
import {GenerateBoard, Authorization, Login, Registration, Messages} from "./components/index";
import './index.css';

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" exact element={<Authorization/>} />
                <Route path="/game" element={<GenerateBoard />} />
                <Route path="/sign-up" element={<Registration/>} />
                <Route path="/login" element={<Login />}/>
                <Route path="/messages" element={<Messages/>}/>
            </Routes>
        </BrowserRouter>
    );
};

export default App
